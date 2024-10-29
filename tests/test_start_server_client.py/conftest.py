import pytest
from unittest.mock import patch
from socket_chat.client import Client
from socket_chat.server import Server
from socket_chat.tsdict import ThreadSafeDict
from queue import Queue
from time import sleep
import threading



@pytest.fixture(scope='function')
def test_server():
    added_clients = Queue()
    removed_clients = Queue()

    def new_add(self, key, value):
        with self.lock:
            if key not in self.dictionary:
                self.dictionary[key] = value
                added_clients.put(key)
                return True
            return False
        
    def new_delitem(self, key):
        with self.lock:
            if key in self.dictionary:
                del self.dictionary[key]
                removed_clients.put(key)

    with patch.object(ThreadSafeDict, 'add_if_not_exists', new=new_add), \
         patch.object(ThreadSafeDict, '__delitem__', new=new_delitem):
        server = Server(54321)
        threading.Thread(target=server.start_server, daemon=True).start()
        sleep(0.5)
        yield server, added_clients, removed_clients
    if server:
        server.server_socket.close()
        sleep(0.5)


@pytest.fixture(scope='function')
def test_client():
    input_queue = Queue()

    with patch('builtins.input', side_effect=lambda _: input_queue.get()):
        client = Client(54321)
        threading.Thread(target=client.connect_to_server, daemon=True).start()
        sleep(0.5)
        yield client, input_queue
    if client:
        client.sock.close()
        sleep(0.5)
