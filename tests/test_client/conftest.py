import pytest
import socket
from socket_chat.tsdict import ThreadSafeDict
from socket_chat.server import ClientHandler
from socket_chat.connection import Connection
import threading


@pytest.fixture(scope='session', autouse=True)
def server():
    threading.Thread(target=start_server, args=(54321,), daemon=True).start()


def start_server(host_port, host_ip = socket.gethostbyname(socket.gethostname())):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((host_ip, host_port))
        server_socket.listen()
        print('[*]Server is listening...\n')
    except Exception as e:
        print(f'[-]Error while starting the server: {e}')
        server_socket.close()

    clients = ThreadSafeDict()
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
            print(f"[*]Accepted connection from {client_addr[0]}:{client_addr[1]}")
            handler = ClientHandler(Connection(client_socket), clients)
            threading.Thread(target=handler.run, daemon=True).start()
        except Exception as e:
            print(f'[-]Error while accepting the client: {e}')
            client_socket.close() 