import tkinter as tk
from tkinter import messagebox
import os
import random
import asyncio
import websockets
import json

ROWS, COLS = 6, 8
TOTAL_CARDS = ROWS * COLS
PAIRS = TOTAL_CARDS // 2
IMG_PATH = "imagens"
SERVER_URI = "ws://localhost:127.0.0.1"

class JogoMemoria:
    def __init__(self, root):
        self.root = root
        self.root.title("Jogo da Memória NFL")
        self.root.attributes('-fullscreen', True)
        self.root.bind("<Escape>", self.sair_fullscreen)

        self.verso_img = tk.PhotoImage(file=os.path.join(IMG_PATH, "verso.png"))
        self.botoes = []
        self.cartas_viradas = []
        self.pontos = {1: 0, 2: 0}
        self.jogador_atual = 1
        self.placar_finalizado = False
        self.websocket = None

        self.menu_frame = self.criar_menu()
        self.jogo_frame = tk.Frame(self.root)
        self.status = tk.Label(self.root, text="", font=("Arial", 14))
        self.reiniciar_btn = tk.Button(self.root, text="Reiniciar", command=self.iniciar_jogo)

        # Iniciar a conexão WebSocket em uma thread separada
        self.start_websocket()

    def start_websocket(self):
        """Inicia a conexão WebSocket em uma thread separada"""
        import threading
        threading.Thread(target=self.run_websocket, daemon=True).start()

    def run_websocket(self):
        """Executa o loop de eventos do WebSocket"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_websocket())

    async def connect_websocket(self):
        """Conecta ao servidor WebSocket"""
        try:
            self.websocket = await websockets.connect(SERVER_URI)
            await self.listen_for_messages()
        except Exception as e:
            print(f"Erro na conexão WebSocket: {e}")

    async def listen_for_messages(self):
        """Ouve mensagens do servidor"""
        try:
            while True:
                message = await self.websocket.recv()
                self.process_message(message)
        except Exception as e:
            print(f"Erro ao ouvir mensagens: {e}")

    def process_message(self, message):
        """Processa mensagem recebida do servidor"""
        data = json.loads(message)
        if data['action'] == 'reveal':
            self.root.after(0, lambda: self.virar_carta(data['index'], notify=False))

    def criar_menu(self):
        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(frame, text="Jogo da Memória NFL", font=("Arial", 24)).pack(pady=20)
        tk.Button(frame, text="JOGAR", font=("Arial", 14), command=self.iniciar_jogo).pack(pady=10)
        tk.Button(frame, text="CRÉDITOS", font=("Arial", 12), command=self.mostrar_creditos).pack(pady=5)
        tk.Button(frame, text="SAIR", font=("Arial", 12), command=self.sair_app).pack(pady=5)

        self.creditos_label = tk.Label(frame, text="", font=("Arial", 10))
        return frame

    def mostrar_creditos(self):
        self.creditos_label.config(text="Desenvolvido por: Ana Laura, Heitor Ceolin e Gabriel Ferreira")
        self.creditos_label.pack()

    def iniciar_jogo(self):
        self.menu_frame.pack_forget()
        self.jogo_frame.pack()
        self.status.pack()
        self.reiniciar_btn.pack(pady=5)

        self.botoes.clear()
        self.cartas_viradas.clear()
        self.pontos = {1: 0, 2: 0}
        self.jogador_atual = 1
        self.placar_finalizado = False

        for widget in self.jogo_frame.winfo_children():
            widget.destroy()

        self.caminhos = [f"{i}.png" for i in range(1, PAIRS + 1)] * 2
        random.shuffle(self.caminhos)
        self.imagens = [tk.PhotoImage(file=os.path.join(IMG_PATH, path)) for path in self.caminhos]

        for i in range(TOTAL_CARDS):
            btn = tk.Button(self.jogo_frame, image=self.verso_img, command=lambda idx=i: self.virar_carta(idx))
            btn.grid(row=i // COLS, column=i % COLS, padx=2, pady=2)
            self.botoes.append(btn)

        self.atualizar_info()

    def virar_carta(self, idx, notify=True):
        if self.botoes[idx]["state"] == "disabled" or idx in self.cartas_viradas or len(self.cartas_viradas) >= 2:
            return

        self.botoes[idx].config(image=self.imagens[idx])
        self.cartas_viradas.append(idx)

        if notify:
            asyncio.run(self.websocket.send(json.dumps({'action': 'reveal', 'index': idx})))

        if len(self.cartas_viradas) == 2:
            self.root.after(1000, self.verificar_par)

    def verificar_par(self):
        i1, i2 = self.cartas_viradas
        if self.caminhos[i1] == self.caminhos[i2]:
            self.pontos[self.jogador_atual] += 1
            self.botoes[i1].config(state="disabled")
            self.botoes[i2].config(state="disabled")
        else:
            self.botoes[i1].config(image=self.verso_img)
            self.botoes[i2].config(image=self.verso_img)
            self.jogador_atual = 2 if self.jogador_atual == 1 else 1

        self.cartas_viradas.clear()
        self.atualizar_info()

        if all(btn["state"] == "disabled" for btn in self.botoes):
            self.fim_de_jogo()

    def atualizar_info(self):
        self.status.config(text=f"Jogador 1: {self.pontos[1]} | Jogador 2: {self.pontos[2]} | Vez: Jogador {self.jogador_atual}")

    def fim_de_jogo(self):
        if self.placar_finalizado:
            return

        self.placar_finalizado = True
        vencedor = "Empate" if self.pontos[1] == self.pontos[2] else f"Jogador {1 if self.pontos[1] > self.pontos[2] else 2}"
        messagebox.showinfo("Fim de Jogo", f"Vencedor: {vencedor}")
        self.salvar_pontuacao(vencedor)

    def salvar_pontuacao(self, vencedor):
        with open("pontuacoes.txt", "a") as f:
            f.write(f"{vencedor} venceu | Pontos: J1={self.pontos[1]}, J2={self.pontos[2]}\n")

    def reiniciar_jogo(self):
        self.iniciar_jogo()

    def sair_app(self):
        self.root.quit()

    def sair_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)

# Execução
if __name__ == "__main__":
    root = tk.Tk()
    jogo = JogoMemoria(root)
    root.mainloop()