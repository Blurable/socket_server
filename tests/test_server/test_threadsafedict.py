import pytest
import socket_chat.connection as connection
import socket_chat.protocol as protocol
import socket_chat.server as server
from socket_chat.tsdict import ThreadSafeDict
import socket
from queue import Queue
import threading
import time 


usernames_list = ['Artyom', 'Baho', 'Poteha', 'Vlados', 'Diman']
creation_queue = Queue()
leave_queue = Queue()
clients = ThreadSafeDict()


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
    threading.Thread(target=monitor_dict, daemon=True).start()
    for i in range(5):
        threading.Thread(target=start_client, args=(usernames_list[i],),daemon=True).start()
    
    client_sockets = []
    for i in range(len(usernames_list)):
        try:
            client_socket, client_addr = start_server.accept()
            client_sockets.append(client_socket)
            print(f"[*]Accepted connection from {client_addr[0]}:{client_addr[1]}")
            handler = server.ClientHandler(connection.Connection(client_socket), clients)
            threading.Thread(target=handler.run, daemon=True).start()
            assert usernames_list[i] == creation_queue.get()
        except Exception as e:
            print(f'[-]Error while accepting the client: {e}')
            client_socket.close()

    assert clients.copy_keys() == usernames_list
    
    for i in range(len(usernames_list)):
        client_sockets[i].close()
        closed_user = leave_queue.get()
        assert closed_user not in clients.copy_keys()
        assert closed_user in usernames_list

    assert clients == {}


def monitor_dict():
    previous_keys = set(clients.copy_keys())

    while True:
        current_keys = set(clients.copy_keys())
        
        new_values = current_keys - previous_keys
        if new_values:
            for key in new_values:
                creation_queue.put(key)
        
        removed_values = previous_keys - current_keys
        if removed_values:
            for key in removed_values:
                leave_queue.put(key)
        
        previous_keys = current_keys
        
