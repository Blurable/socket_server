import pytest
import socket


@pytest.fixture(scope='session', autouse=True)
def start_server(host_ip = socket.gethostbyname(socket.gethostname())):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((host_ip, 54321))
        server_socket.listen()
        print('[*]Server is listening...\n')
    except Exception as e:
        print(f'[-]Error while starting the server: {e}')
        server_socket.close()
    return server_socket
    

