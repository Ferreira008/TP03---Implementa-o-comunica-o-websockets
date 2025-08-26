JOGO DA MEMÓRIA - DOCUMENTAÇÃO DO PROJETO

Autores:
- ANA LAURA DA SILVA NASCIMENTO
- GABRIEL FERREIRA DE SOUSA
- HEITOR CEOLIN RIBEIRO

Instruções de Execução:
MODOS:
-INTERFACE
1. Certifique-se de ter Python 3.8+ instalado em sua máquina.
2. Instale as dependências necessárias com o comando no CMD:
   pip install customtkinter pillow tk
3. Extraia o conteúdo do arquivo Jogo_NFL.zip para uma pasta local.
4. Navegue até o diretório do projeto no terminal.
5. Execute o arquivo principal por meio da IDE de sua preferência. 
6. A interface do jogo será exibida. Siga as instruções na tela para jogar.


-TERMINAL
O jogo pode ser jogado no modo multiplayer via terminal, utilizando servidor.py e jogo.py.
- SERVIDOR:
- Abrir o prompt de comando na pasta do projeto e execute o comando:
- python3 servidor.py 

- CLIENTE:
- No Linux, instale o suporte a ambiente virtuais (caso necessário):
- sudo apt install python3-venv
- python3  -m venv venv
- source venv\bin\activate
- python jogo.py 



Ferramentas Utilizadas:
- Linguagem: Python 3.8+
- Bibliotecas:
  - Customtkinter: interface gráfica moderna e personalizável
  - Tkinter: base da interface gráfica
  - Pillow (PILL): manipulação de imagens das cartas
  - Random: aleatorização do deck de cartas
  - Asyncio: execução de código assíncrono.
  - Webscokets: comunicação em tempo real entre cliente e servidor.


Funcionalidades Implementadas:
- Tabuleiro com 6 linhas e 8 colunas (48 cartas)
- Cada carta possui um par idêntico.
- Sistema de turnos alternados entre dois jogadores
- Verificação automática de pares corretos (mantém virados) ou incorretos (vira novamente após 1 segundo)
- Placar exibido em tempo real para ambos os jogadores. 
- Vencedor definido automaticamente ao final da partida.
- Botão de reinício da partida.
- Design visual com imagens e componentes personalizados.
- Modo player x player online via websockets.


Descrição Geral:
Este projeto consiste em uma aplicação interativa que simula o clássico jogo da memória, permitindo que dois jogadores participem de forma alternada. Desenvolvido como parte de uma atividade prática, o jogo visa reforçar conceitos fundamentais de programação, tais como controle de fluxo, manipulação de matrizes, estruturas condicionais, comunicações websocket e boas práticas de desenvolvimento com interface gráfica.

Objetivo:
Criar um jogo funcional da memória que permita a dois jogadores competirem entre si, identificando pares de cartas com o menor número de tentativas possível. O jogo mantém placar e alternância de turnos, indicando o vencedor ao final da partida.

Estrutura do Projeto:
- O projeto contém 2 arquivos e uma pasta:
- servidor.py : gerencia conexões, regras do jogo e turnos.
- jogo.py : cliente/inteface gráfica, envia comandos ao servidor
- imagens/ : pasta com as imagens das cartas e verso delas.
- As imagens das cartas estão organizadas para permitir emparelhamento.
- Interface gráfica com botões, controle de turnos e pontuação visível.
