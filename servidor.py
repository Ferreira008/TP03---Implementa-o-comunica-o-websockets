import asyncio
import websockets
import random
import sys

ROWS, COLS = 6, 8  # configuração original (48 cartas)
PAIRS = ROWS * COLS // 2

# Estado global
tabuleiro = []
visivel = []
pontuacao = [0, 0]
vez = 0
jogadas = []  # jogadas temporárias [(row,col,valor), ...]
player_sockets = []  # sockets dos jogadores (0 e 1)

# --- utilitários ---

def gerar_tabuleiro():
    """Gera um tabuleiro com valores '1'..'PAIRS' (cada par duplicado)."""
    vals = [str(i) for i in range(1, PAIRS + 1)]
    baralho = vals * 2
    random.shuffle(baralho)
    # retorna matriz ROWS x COLS
    return [baralho[i * COLS:(i + 1) * COLS] for i in range(ROWS)]

def reset_estado():
    global tabuleiro, visivel, pontuacao, vez, jogadas
    tabuleiro = gerar_tabuleiro()
    visivel = [['##' for _ in range(COLS)] for _ in range(ROWS)]
    pontuacao = [0, 0]
    vez = 0
    jogadas = []

def fim_de_jogo():
    return all(visivel[r][c] != '##' for r in range(ROWS) for c in range(COLS))

def formatar_estado_tabuleiro():
    linhas = []
    for r in range(ROWS):
        linhas.append('\t'.join(visivel[r]))
    return "BOARD\n" + '\n'.join(linhas)

async def sendln(ws, msg: str):
    await ws.send(msg)

async def broadcast(msg: str):
    for ws in list(player_sockets):
        try:
            await sendln(ws, msg)
        except:
            pass

# --- lógica do jogo ---

async def processar_turno(jogador, row, col):
    global vez, jogadas, pontuacao, visivel

    # valida vez
    if jogador != vez:
        await sendln(player_sockets[jogador], "ERRO Não é sua vez")
        return

    # valida coordenadas
    if not (0 <= row < ROWS and 0 <= col < COLS):
        await sendln(player_sockets[jogador], "ERRO posição inválida")
        return

    # valida se já está visível
    if visivel[row][col] != '##':
        await sendln(player_sockets[jogador], "ERRO posição inválida")
        return

    valor = tabuleiro[row][col]
    visivel[row][col] = valor
    jogadas.append((row, col, valor))

    # notifica todos da carta virada
    await broadcast(f"CARD {row} {col} {valor}")
    await broadcast(formatar_estado_tabuleiro())

    # se duas cartas foram jogadas, avalia
    if len(jogadas) == 2:
        await asyncio.sleep(1)  # deixa cliente mostrar a segunda carta
        (r1, c1, v1), (r2, c2, v2) = jogadas

        if v1 == v2:
            await broadcast("MATCH")
            pontuacao[jogador] += 1
        else:
            await broadcast("NO_MATCH")
            # esconde novamente
            visivel[r1][c1] = '##'
            visivel[r2][c2] = '##'
            vez = 1 - vez  # troca a vez

        await broadcast(f"SCORE {pontuacao[0]} {pontuacao[1]}")
        await broadcast(formatar_estado_tabuleiro())
        jogadas.clear()

        if fim_de_jogo():
            if pontuacao[0] > pontuacao[1]:
                await broadcast("WINNER 1")
            elif pontuacao[1] > pontuacao[0]:
                await broadcast("WINNER 2")
            else:
                await broadcast("WINNER DRAW")
            await broadcast("END")
        else:
            # informa quem joga
            await sendln(player_sockets[vez], "YOUR_TURN")
            await sendln(player_sockets[1 - vez], "WAIT")

# --- mensagens do cliente ---

async def tratar_mensagem(jogador, msg):
    partes = msg.strip().split()
    if not partes:
        return
    comando = partes[0].upper()

    if comando == "CONNECT":
        # boas-vindas
        if jogador == 0:
            await sendln(player_sockets[0], "WELCOME PLAYER 1")
            await sendln(player_sockets[0], "AGUARDE o outro jogador...")
        elif jogador == 1:
            await sendln(player_sockets[1], "WELCOME PLAYER 2")

        # inicia quando ambos estão conectados
        if len(player_sockets) == 2:
            reset_estado()
            await broadcast("START")
            await broadcast(formatar_estado_tabuleiro())
            await sendln(player_sockets[vez], "YOUR_TURN")
            await sendln(player_sockets[1 - vez], "WAIT")

    elif comando == "TURN":
        if len(partes) != 3 or not partes[1].isdigit() or not partes[2].isdigit():
            await sendln(player_sockets[jogador], "ERRO comando inválido")
            return
        row, col = int(partes[1]), int(partes[2])
        await processar_turno(jogador, row, col)

    elif comando == "END":
        await broadcast("END digitado. Jogador desconectado, encerrando.")
        print(f"Encerrando o jogo por comando END do jogador {jogador}.")
        for ws in list(player_sockets):
            try:
                await ws.close()
            except:
                pass
        player_sockets.clear()
        print("Jogo encerrado.")

    else:
        await sendln(player_sockets[jogador], "ERRO comando inválido")

# --- gerenciamento de conexões ---

async def handler(ws):
    if len(player_sockets) >= 2:
        await sendln(ws, "ERRO sala cheia")
        await ws.close()
        return

    jogador = len(player_sockets)
    player_sockets.append(ws)
    print(f"Jogador {jogador+1} conectado.")

    try:
        async for msg in ws:
            await tratar_mensagem(jogador, msg)
    except websockets.ConnectionClosed:
        print(f"Jogador {jogador+1} desconectado.")
        if ws in player_sockets:
            player_sockets.remove(ws)

# --- main ---

async def main_server(host="127.0.0.1", port=8765):
    async with websockets.serve(handler, host, port):
        print(f"Servidor rodando em ws://{host}:{port}")
        await asyncio.Future()

if __name__ == "__main__":
    # aceita ip porta como args, senão usa padrão
    if len(sys.argv) == 3:
        h = sys.argv[1]
        p = int(sys.argv[2])
        asyncio.run(main_server(h, p))
    else:
        asyncio.run(main_server())
