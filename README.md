JOGO DA MEMÓRIA - DOCUMENTAÇÃO DO PROJETO

Autores:
- ANA LUISA RODRIGUES DINIZ
- ARTHUR EXPEDITO ARAÚJO FERREIRA
- BEATRIZ OLIVEIRA SANTOS
- ÍTALO RODRIGUES GONTIJO

Instruções de Execução:
MODOS:
-INTERFACE
1. Certifique-se de ter Python 3.x instalado em sua máquina.
2. Instale as dependências necessárias com o comando no CMD:
   pip install customtkinter pillow tk
3. Extraia o conteúdo do arquivo JOGO_MEM.zip para uma pasta local.
4. Navegue até o diretório do projeto no terminal.
5. Execute o arquivo principal por meio da IDE de sua preferência. Para melhor esclarecimento, segue o vídeo:
   [Tutorial de execução](https://drive.google.com/file/d/1GmyOu1hvrWvr5lAp8olS28XQwZP0rvqE/view?usp=sharing)
6. A interface do jogo será exibida. Siga as instruções na tela para jogar.


-TERMINAL
O jogo é dividido entre servidor e player. O servidor deve ser executando em um sistema Windows 10 ou 11.
O código player deve ser executado em distribuições linux. Recomenda-se Ubuntu.
- SERVIDOR:
- Abrir o prompt de comando e digitar o comando:
- python3 <local do download>\C:\Users\italo\Desktop\JOGO_MEM-main\Python\Servidor_terminal\server.py <ip> <porta>
- Os ips e portas utilizados para teste são:
- ip: 25.33.40.142
- porta: 8080

- PLAYER:
- Abrir o terminal e executar os comandos:
- sudo apt install python3-venv
- python3  -m venv <local do download>
- source <caminho colocado no comando acima>\bin\activate
- python3 <caminho do download>\C:\Users\italo\Desktop\JOGO_MEM-main\Python\Servidor_terminal\player.py <ip do servidor> <porta do servidor>



Ferramentas Utilizadas:
- Linguagem: Python 3.x
- Bibliotecas:
  - customtkinter: para construção da interface gráfica moderna e personalizável
  - tkinter: base da interface gráfica
  - PIL (Pillow): manipulação de imagens das cartas
  - Random: Aleatorização do deck de cartas
  - aioconsole: Interação assícrona, sem necessidade de pausa, com funções async
  - asyncio: Execução de código de forma assíncrona, de forma local, sem servidor
  - Websockets: Comunicação em tempo real e bidirecional com conexão entre os pontos


Funcionalidades Implementadas:
- Tabuleiro com 6 linhas e 8 colunas (48 cartas)
- Cada carta possui um par idêntico, representado por cartas de baralho
- Sistema de turnos alternados entre dois jogadores
- Verificação automática de pares corretos (mantém virados) ou incorretos (vira novamente após 1 segundo)
- Placar exibido em tempo real
- Determinação automática do vencedor
- Tela final exibindo resultado
- Botão de reinício de partida
- Armazenamento de nomes durante a partida
- Design visual adaptado com imagens e componentes personalizados via CustomTkinter
- Modo player x player online, por meio de comunicação websockets via terminal


Descrição Geral:
Este projeto consiste em uma aplicação interativa que simula o clássico jogo da memória, permitindo que dois jogadores participem de forma alternada. Desenvolvido como parte de uma atividade prática, o jogo visa reforçar conceitos fundamentais de programação, tais como controle de fluxo, manipulação de matrizes, estruturas condicionais, comunicações websocket e boas práticas de desenvolvimento com interface gráfica.

Objetivo:
Criar um jogo funcional da memória que permita a dois jogadores competirem entre si, identificando pares de cartas com o menor número de tentativas possível. O jogo mantém placar e alternância de turnos, indicando o vencedor ao final da partida.

Estrutura do Projeto:
- O projeto contém arquivos distintos, divididos entre INTERFACE nomeados de "main.py" , "board.py" e "result.py" e SERVIDOR\TERMINAL nomeados de server.py e player.py.
- As imagens das cartas estão organizadas para permitir emparelhamento.
- Interface gráfica com botões, controle de turnos e pontuação visível.