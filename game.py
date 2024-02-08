import os
import socket
import json
import time
import sys
import signal
import platform
import errno

from colorama import Fore, Back, init

# Variáveis
init(autoreset=True)
vel = 0
dados_recebidos = None
clientClass = None
local_os = platform.system()


def colorant(text, color, load):
    global vel
    if load == 0:
        vel = .050
    elif load == 1:
        vel = 0
    else:
        vel = 0
    for letra in text:
        print(color + letra, end='', flush=True)
        time.sleep(vel)  # Ajuste o atraso conforme necessário
    print(Fore.RESET + Back.RESET)  # Reset as cores para o padrão


def interrupt(signum, frame):
    colorant("\n Informação: Sinal de interrupção recebido. Executando operações de encerramento...",
             Fore.BLACK + Back.LIGHTBLUE_EX, 1)
    client_socket.close()
    sys.exit(0)


# Configurações locais
signal.signal(signal.SIGINT, interrupt)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


while True:

    if local_os == 'Windows':
        os.system("cls")
    elif local_os == 'Linux' or 'Darwin':
        os.system("clear")

    try:

        port = int(input("> Digite a porta fornecida por email: "))
        client_id = input("> Digite seu ID: ")
        mensagem = {
            'client_id': client_id,
            'windowClass': 'mainWindow'
        }
        client_socket.connect(('localhost', port))
        client_socket.sendall(json.dumps(mensagem).encode('utf-8'))

    except socket.timeout:

        client_socket.close()
        colorant(
            "\n Erro: Tempo de conexão atingido. Tente novamente.",
            Fore.BLACK + Back.LIGHTRED_EX, 0)
        input(" Pressione 'enter' para continuar.")
        continue

    except ConnectionRefusedError:

        colorant(
            "\n Erro: A conexão foi recusada. Verifique se digitou a porta corretamente e tente novamente.",
            Fore.BLACK + Back.LIGHTRED_EX, 0)
        input(" Pressione 'enter' para continuar.")
        continue

    except OSError as e:

        client_socket.close()
        if e.errno == errno.EBADF:

            colorant(
                "\n Erro: Você digitou caracteres inválidos. Tente novamente.",
                Fore.BLACK + Back.LIGHTRED_EX, 0)
            input(" Pressione 'enter' para continuar.")
            continue

        else:

            colorant(
                "\n Erro: Ocorreu um erro a nível de sistema. Tente novamente.",
                Fore.BLACK + Back.LIGHTRED_EX, 0)
            print(f" Código de erro: {e.errno}")
            input(" Pressione 'enter' para continuar.")
            continue

    except ValueError:

        colorant(
            "\n Erro: Você digitou caracteres inválidos. Tente novamente.",
            Fore.BLACK + Back.LIGHTRED_EX, 0)
        input(" Pressione 'enter' para continuar.")
        continue

    except Exception as e:

        client_socket.close()
        colorant(
            "\n Erro: Ocorreu algo inesperado. Envie o código de erro por email.",
            Fore.BLACK + Back.LIGHTRED_EX, 0)
        print(f" Código de erro: {e}")
        input(" Pressione 'enter' para continuar.")
        continue

    dados_recebidos = client_socket.recv(1024)

    try:

        client_data = json.loads(dados_recebidos.decode('utf-8'))
        clientClass = client_data.get('clientClass')
        connectionStatus = client_data.get('connectionStatus')

        if connectionStatus == 'mainApp_OK':
            break

        elif connectionStatus == 'mainApp_refused_ID_already_used':

            client_socket.close()
            colorant("\n Erro (Conexão recusada): Esse ID já foi utilizado por outro jogador. Tente novamente.",
                     Fore.BLACK + Back.LIGHTRED_EX, 0)
            input(" Pressione 'enter' para continuar.")
            continue

        elif connectionStatus == 'mainApp_refused_Invalid_ID':

            client_socket.close()
            colorant("\n Erro (Conexão recusada): ID inválido. Tente novamente.",
                     Fore.BLACK + Back.LIGHTRED_EX, 0)
            input(" Pressione 'enter' para continuar.")
            continue

        elif connectionStatus == 'mainApp_refused_Player_limit_reached':

            client_socket.close()
            colorant(
                "\n Erro (Conexão recusada): Limite de jogadores atingido. Tente usar '01010' para entrar como "
                "espectador.",
                Fore.BLACK + Back.LIGHTRED_EX, 0)
            input(" Pressione 'enter' para continuar.")
            continue

        else:

            client_socket.close()
            colorant(
                "\n Erro (Conexão recusada): O erro é desconhecido. Informe a equipe por email.",
                Fore.BLACK + Back.LIGHTRED_EX, 0)
            input(" Pressione 'enter' para continuar.")
            continue

    except Exception as e:

        colorant("Erro: Não foi possível processar os dados do servidor.",
                 Fore.BLACK + Back.LIGHTRED_EX, 0)
        print(f" Código de erro: {e}")
        input(" Pressione 'enter' para continuar.")
        continue


if clientClass == '0':

    print("Olá! Você é um jogador.")

    while True:

        numero = int(input("Digite um número: "))
        mensagem = {
            'numero': numero
        }
        client_socket.sendall(json.dumps(mensagem).encode('utf-8'))

        data = client_socket.recv(1024)
        if not data:
            break

        resposta = json.loads(data.decode('utf-8'))
        soma_servidor = resposta.get('soma')
        print(f"Soma atual no servidor: {soma_servidor}")

elif clientClass == '1':

    print("Olá! Você é um espectador. Aguarde pelos resultados.")

    while True:

        data = client_socket.recv(1024)
        if not data:
            break

        resposta = json.loads(data.decode('utf-8'))
        soma_servidor = resposta.get('soma')
        print(f"Soma atual no servidor para espectadores: {soma_servidor}")

else:

    client_socket.close()
    sys.exit()

# Fechando a conexão do cliente se houver desconexão ou se o jogo foi encerrado
colorant("Alerta: O jogo foi encerrado ou você perdeu a conexão.", Fore.BLACK + Back.LIGHTYELLOW_EX, 0)
client_socket.close()
