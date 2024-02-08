import socket
import json
import threading
import time

# Dicionário de IDs de usuários
user_id = {
    "01010": "Convidado",
}
# !!! DICIONÁRIO EXCLUÍDO PARA MANTER A PRIVACIDADE DOS JOGADORES.

# Variável utilizadas no script inteiro
jogadores = []
jogadores_responderam = []
espectadores = []
ids_ativos = set()
rodada_atual = 0
soma_atual = 0
max_jogadores = len(user_id) - 1
lock = threading.Lock()

# Configurando o socket
porta = 49163
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', porta))
server_socket.listen()
print(f"Aguardando conexões...  Porta para ligar o servidor: {porta}")


def handle_jogador(client_id, client_socket, client_address, lock):
    global soma_atual, jogadores_responderam

    while True:

        data = client_socket.recv(1024)
        if not data:
            connection_close(client_id, client_socket, client_address)
            break

        data = json.loads(data.decode('utf-8'))
        numero_recebido = 0
        numero_recebido = data.get('numero')
        print(f"Número '{numero_recebido}' recebido de {client_address}. ")

        # Somando número recebido
        with lock:
            soma_atual += numero_recebido
            print(f"Estado do resultado do servidor: {soma_atual}")
            jogadores_responderam.append(client_socket)


def handle_espectador():
    while True:
        data = client_socket.recv(1024)
        if not data:
            connection_close(client_id, client_socket, client_address)
            break


def enviar_resposta():
    global jogadores_responderam, ids_ativos, rodada_atual

    while True:

        if len(jogadores_responderam) == len(ids_ativos) and len(ids_ativos) == max_jogadores:

            print(f"Todos os jogadores responderam. Enviando resposta para os clientes...")
            rodada_atual += 1
            resultado = {
                'soma': soma_atual,
                'rodada': rodada_atual
            }

            aux = 0
            for jogador_socket in jogadores:
                aux += 1
                print(f"Resultado 'RD{rodada_atual};S{soma_atual}' enviado para o cliente {aux}. ")
                jogador_socket.sendall(json.dumps(resultado).encode('utf-8'))
                if jogador_socket in jogadores_responderam:
                    jogadores_responderam.remove(jogador_socket)

            aux = 0
            for espectador_socket in espectadores:
                aux -= 1
                print(f"Resultado 'RD{rodada_atual};S{soma_atual}' enviado para o cliente {aux}. ")
                espectador_socket.sendall(json.dumps(resultado).encode('utf-8'))

        time.sleep(1)


def connection_close(client_id, client_socket, client_address):
    global jogadores_responderam

    if client_id != '01010':
        print(f"A conexão com {client_address} foi perdida. Jogador removido das listas.")
        ids_ativos.remove(client_id)
        jogadores.remove(client_socket)
        if client_socket in jogadores_responderam:
            jogadores_responderam.remove(client_socket)
        client_socket.close()
    else:
        print(f"A conexão com {client_address} foi perdida. Espectador removido das listas.")
        espectadores.remove(client_socket)
        client_socket.close()


# Iniciando Threads de controle do servidor
threading.Thread(target=enviar_resposta).start()

while True:

    client_socket, client_address = server_socket.accept()
    print(f"Conexão estabelecida com {client_address}")
    message = client_socket.recv(1024)
    try:
        mensagem = json.loads(message.decode('utf-8'))
    except Exception as e:
        mensagem = {
            'windowClass': None,
            'client_id': 0,
            'err': e
        }

    windowClass = mensagem.get('windowClass')
    client_id = mensagem.get('client_id')

    if windowClass == 'mainWindow':

        # A conexão foi aceita. Este bloco adiciona o espectador no jogo e cria uma Thread para lidar com ele.
        if client_id == '01010':

            espectadores.append(client_socket)
            client_info = {
                'clientClass': '1',
                'connectionStatus': 'mainApp_OK'
            }
            client_socket.sendall(json.dumps(client_info).encode('utf-8'))
            print(f"{client_address} com o ID {client_id} é um espectador.")
            threading.Thread(target=handle_espectador).start()

        # Verifica se o limite de jogadores foi atingido
        elif len(ids_ativos) > max_jogadores:

            print(f"Conexão recusada para {client_address}. Limite de jogadores atingido.")
            client_info = {
                'clientClass': '2',
                'connectionStatus': 'mainApp_refused_Player_limit_reached'
            }
            client_socket.sendall(json.dumps(client_info).encode('utf-8'))
            client_socket.close()

        # Verifica se o ID é válido
        elif client_id not in user_id:

            print(f"Conexão recusada para {client_address}. ID inválido ({client_id}).")
            client_info = {
                'connectionStatus': 'mainApp_refused_Invalid_ID',
                'clientClass': '2'
            }
            client_socket.sendall(json.dumps(client_info).encode('utf-8'))
            client_socket.close()

        # Verifica se o ID já foi utilizado
        elif client_id in ids_ativos:

            print(f"Conexão recusada para {client_address}. ID já em uso ({client_id}).")
            client_info = {
                'connectionStatus': 'mainApp_refused_ID_already_used',
                'clientClass': '2'
            }
            client_socket.sendall(json.dumps(client_info).encode('utf-8'))
            client_socket.close()

        # A conexão foi aceita. Esse bloco adiciona o jogador no jogo e cria uma Thread para lidar com ele.
        elif client_id in user_id and client_id != '01010':

            print(f"Conexão aceita para {client_address}.")
            print(f"O cliente {client_address} com o ID {client_id} é um jogador ativo.")
            ids_ativos.add(client_id)
            jogadores.append(client_socket)
            threading.Thread(target=handle_jogador, args=(
                client_id, client_socket, client_address, lock)).start()
            client_info = {
                'clientClass': '0',
                'connectionStatus': 'mainApp_OK'
            }
            client_socket.sendall(json.dumps(client_info).encode('utf-8'))

        # Um erro desconhecido ocorreu
        else:

            print(f"Conexão recusada para {client_address}. Erro desconhecido.")
            client_info = {
                'connectionStatus': 'mainApp_refused',
                'clientClass': '2'
            }
            client_socket.sendall(json.dumps(client_info).encode('utf-8'))
            client_socket.close()

    # A conexão foi recusada. Provavelmente o cliente conectado não executa um programa compatível.
    else:

        print(f"Conexão recusada para {client_address}. Dados não compatíveis.")
        client_socket.close()
