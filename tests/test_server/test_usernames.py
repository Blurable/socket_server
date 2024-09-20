import pytest
import socket_chat.connection as connection
import socket_chat.protocol as protocol
import socket_chat.server as server
from socket_chat.tsdict import ThreadSafeDict
import socket
from queue import Queue
import threading
import time 


username_list = ['Artyom', 'Baho', 'Poteha', 'Vlados', 'Diman']
creation_queue = Queue()
leave_queue = Queue()

def start_client(username):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((socket.gethostbyname(socket.gethostname()), 54321))
    conn = connection.Connection(client_socket)

    pkt = protocol.chat_connect()
    pkt.username = username
    conn.send(pkt.pack())
    while True:
        try:
            conn.recv(1)
        except:
            pass
    
    

def test_client_usernames(start_server):
    for i in range(5):
        threading.Thread(target=start_client, args=(username_list[i],),daemon=True).start()
    
    clients = ThreadSafeDict()
    client_sockets = []
    for i in range(5):
        try:
            client_socket, client_addr = start_server.accept()
            client_sockets.append(client_socket)
            print(f"[*]Accepted connection from {client_addr[0]}:{client_addr[1]}")
            handler = server.ClientHandler(connection.Connection(client_socket), clients)
            threading.Thread(target=handler.run, daemon=True).start()
        except Exception as e:
            print(f'[-]Error while accepting the client: {e}')
            client_socket.close()
    time.sleep(1)
    assert len(clients) == 5
    client_sockets[1].close()
    time.sleep(1)
    assert len(clients) == 4