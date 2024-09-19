import pytest
import socket_chat.connection as connection
import socket_chat.server as server
from socket_chat.tsdict import ThreadSafeDict
import threading
import socket


@pytest.fixture(scope='session')
def clients_dict():
    clients_dict = ThreadSafeDict()
    return clients_dict


@pytest.fixture(scope='session', autouse=True)
def test_server(clients_dict):
    threading.Thread(target=start_server, args=(clients_dict, 54321,), daemon=True).start()


def start_server(clients_dict, host_port, host_ip = socket.gethostbyname(socket.gethostname())):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((host_ip, host_port))
        server_socket.listen()
        print('[*]Server is listening...\n')
    except Exception as e:
        print(f'[-]Error while starting the server: {e}')
        server_socket.close()
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
            print(f"[*]Accepted connection from {client_addr[0]}:{client_addr[1]}")
            handler = server.ClientHandler(connection.Connection(client_socket), clients_dict)
            threading.Thread(target=handler.run, daemon=True).start()
        except Exception as e:
            print(f'[-]Error while accepting the client: {e}')
            client_socket.close()

