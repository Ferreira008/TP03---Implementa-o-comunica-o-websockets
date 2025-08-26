import tkinter as tk
from tkinter import messagebox
import os
import asyncio
import websockets
import threading

ROWS, COLS = 6, 8
TOTAL_CARDS = ROWS * COLS
PAIRS = TOTAL_CARDS // 2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "imagens")

SERVER_URI = "ws://127.0.0.1:8765"  # padrão, ajuste se necessário

class JogoMemoria:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Memória NFL")
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.sair_fullscreen)

        # imagens
        verso_path = os.path.join(IMG_PATH, "verso.png")
        if os.path.exists(verso_path):
            self.verso_img = tk.PhotoImage(file=verso_path)
        else:
            # fallback simples
            self.verso_img = tk.PhotoImage(width=120, height=160)

        self.card_images = {}  # mapa valor -> PhotoImage (carregado sob demanda)

        # UI: menu
        self.menu_frame = self.criar_menu()
        # UI: container do jogo (criado mas não preenchido)
        self.jogo_frame = tk.Frame(self.root)

        # variáveis de jogo cliente
        self.buttons = []  # matriz ROWS x COLS de botões
        self.pending = []  # cartas reveladas aguardando MATCH/NO_MATCH [(row,col), ...]
        self.player_id = None
        self.can_play = False
        self.websocket = None
        self.loop = None

        # área de status e controles (na interface do jogo)
        self.info_label = None
        self.score_label = None
        self.reiniciar_btn = None

        # inicia websocket em thread separada
        threading.Thread(target=self.run_websocket, daemon=True).start()

    def criar_menu(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text="Jogo da Memória NFL", font=("Arial", 24)).pack(pady=20)
        tk.Button(frame, text="JOGAR", font=("Arial", 14), command=self.pedir_conexao).pack(pady=10)
        tk.Button(frame, text="CRÉDITOS", font=("Arial", 12), command=self.mostrar_creditos).pack(pady=5)
        tk.Button(frame, text="SAIR", font=("Arial", 12), command=self.sair_app).pack(pady=5)

        self.creditos_label = tk.Label(frame, text="", font=("Arial", 10))
        return frame

    def mostrar_creditos(self):
        self.creditos_label.config(text="Desenvolvido por: Ana Laura, Heitor Ceolin e Gabriel Ferreira")
        self.creditos_label.pack()

    def pedir_conexao(self):
        """Botão JOGAR: envia CONNECT ao servidor (assume websocket já conectado)."""
        if self.websocket is None:
            messagebox.showwarning("Aguarde", "Ainda conectando ao servidor. Espere alguns segundos e clique novamente.")
            return
        # envia CONNECT
        asyncio.run_coroutine_threadsafe(self.websocket.send("CONNECT"), self.loop)
        self.info_temp("Conectando ao servidor... Aguardando outro jogador.")

    def criar_interface_jogo(self):
        """Cria a interface do jogo (frames, canvas rolável, painel lateral)."""
        # limpa menu e monta jogo_frame
        self.menu_frame.pack_forget()
        self.jogo_frame.pack(expand=True, fill="both")

        # layout: esquerda = canvas rolável com cartas, direita = painel de controles
        left = tk.Frame(self.jogo_frame)
        left.pack(side="left", fill="both", expand=True)
        right = tk.Frame(self.jogo_frame, width=260)
        right.pack(side="right", fill="y")

        # canvas com frame interno para grid
        canvas = tk.Canvas(left)
        vsb = tk.Scrollbar(left, orient="vertical", command=canvas.yview)
        hsb = tk.Scrollbar(left, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor='nw')

        # cria botões (grid) dentro do inner frame
        self.buttons = []
        for r in range(ROWS):
            row_btns = []
            for c in range(COLS):
                btn = tk.Button(inner, image=self.verso_img,
                                command=lambda rr=r, cc=c: self.on_card_click(rr, cc))
                btn.grid(row=r, column=c, padx=6, pady=6)
                row_btns.append(btn)
            self.buttons.append(row_btns)

        def _on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", _on_config)

        # painel lateral: informações e botões
        self.info_label = tk.Label(right, text="Aguardando início...", font=("Arial", 12))
        self.info_label.pack(pady=10)
        self.score_label = tk.Label(right, text="Placar: J1=0 | J2=0", font=("Arial", 12))
        self.score_label.pack(pady=10)
        self.reiniciar_btn = tk.Button(right, text="Reiniciar (local)", command=self.pedir_reinicio)
        self.reiniciar_btn.pack(pady=10)
        tk.Button(right, text="Sair", command=self.sair_app).pack(pady=10)

    def pedir_reinicio(self):
        # envia END para reiniciar a partida (o servidor trata desconexão)
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.send("END"), self.loop)

    def info_temp(self, text):
        if self.info_label:
            self.info_label.config(text=text)
        else:
            # enquanto menu, mostra mensagem temporária
            messagebox.showinfo("Info", text)

    def on_card_click(self, row, col):
        if not self.can_play:
            self.info_temp("⚠ Não é sua vez!")
            return
        # evita clicar em carta já aberta / desabilitada
        btn = self.buttons[row][col]
        if btn["state"] == "disabled":
            return
        # envia comando TURN (servidor fará validação)
        asyncio.run_coroutine_threadsafe(self.websocket.send(f"TURN {row} {col}"), self.loop)

    # --- rede / websocket ---

    def run_websocket(self):
        """Thread que roda um event loop asyncio e conecta ao servidor."""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.connect_websocket())
        except Exception as e:
            print("Erro na thread websocket:", e)

    async def connect_websocket(self):
        try:
            async with websockets.connect(SERVER_URI) as ws:
                self.websocket = ws
                print("Conectado ao servidor.")
                # lê mensagens do servidor
                async for message in ws:
                    # repassa ao loop principal do Tk (thread-safe)
                    self.root.after(0, lambda m=message: self.process_message(m))
        except Exception as e:
            print("Erro na conexão WebSocket:", e)
            # tenta reconectar? por simplicidade, informa usuário
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na conexão: {e}"))

    # --- processamento de mensagens do servidor ---

    def process_message(self, msg: str):
        """Interpreta mensagens simples (separadas por espaços)."""
        if not msg:
            return
        parts = msg.strip().split()
        if not parts:
            return
        cmd = parts[0].upper()

        if cmd == "WELCOME":
            # pode receber "WELCOME PLAYER 1"
            if "PLAYER" in parts:
                try:
                    idx = parts.index("PLAYER")
                    pid = int(parts[idx + 1])
                    # padroniza 0-based internamente
                    self.player_id = pid - 1
                    self.info_temp(f"Você é o Jogador {pid}")
                except:
                    pass
            else:
                self.info_temp(msg)

        elif cmd == "AGUARDE":
            self.info_temp("Aguarde o outro jogador...")

        elif cmd == "START":
            # servidor disse para iniciar o jogo: cria UI de jogo se ainda não criada
            if not self.jogo_frame.winfo_ismapped():
                self.crear = getattr(self, "criar_interface_jogo", None)
                self.root.after(0, self.criar_interface_jogo)

        elif cmd == "YOUR_TURN":
            self.can_play = True
            self.info_temp("Sua vez! Clique em uma carta.")

        elif cmd == "WAIT":
            self.can_play = False
            self.info_temp("⏳ Não é sua vez.")

        elif cmd == "CARD":
            # formato: CARD row col valor
            if len(parts) >= 4:
                try:
                    row = int(parts[1])
                    col = int(parts[2])
                    val = parts[3]
                    # carrega imagem correspondente (val.png) se ainda não carregada
                    if val not in self.card_images:
                        path = os.path.join(IMG_PATH, f"{val}.png")
                        if os.path.exists(path):
                            self.card_images[val] = tk.PhotoImage(file=path)
                        else:
                            # placeholder transparente se arquivo não existir
                            self.card_images[val] = self.verso_img
                    # atualiza botão
                    self.buttons[row][col].config(image=self.card_images[val])
                    # registra como revelada temporariamente
                    self.pending.append((row, col))
                except Exception as e:
                    print("Erro no CARD:", e)

        elif cmd == "NO_MATCH":
            # após pequeno delay viram de volta
            self.root.after(800, self._flip_back_pending)

        elif cmd == "MATCH":
            # desabilita os botões das cartas pendentes
            for (r, c) in list(self.pending):
                try:
                    self.buttons[r][c].config(state="disabled")
                except:
                    pass
            self.pending.clear()
            self.info_temp("Acertou um par!")

        elif cmd == "SCORE":
            # SCORE x y
            if len(parts) >= 3:
                j1 = parts[1]; j2 = parts[2]
                self.score_label.config(text=f"Placar: J1={j1} | J2={j2}")

        elif cmd == "BOARD":
            # o servidor envia múltiplas linhas; ignoramos (mantemos UI por mensagens CARD)
            pass

        elif cmd.startswith("WINNER") or cmd == "END":
            # mostra fim de jogo
            texto = " ".join(parts[1:]) if len(parts) > 1 else "Partida encerrada."
            messagebox.showinfo("Fim de Jogo", texto)
            self.info_temp(texto)

        elif cmd.startswith("ERRO"):
            self.info_temp("Erro do servidor: " + " ".join(parts[1:]))

        else:
            # mensagens inesperadas: exibir em log
            print("Mensagem não tratada do servidor:", msg)

    def _flip_back_pending(self):
        for (r, c) in list(self.pending):
            try:
                self.buttons[r][c].config(image=self.verso_img)
            except:
                pass
        self.pending.clear()

    def sair_app(self):
        try:
            self.root.quit()
        except:
            pass

    def sair_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)


if __name__ == "__main__":
    root = tk.Tk()
    jogo = JogoMemoria(root)
    root.mainloop()
