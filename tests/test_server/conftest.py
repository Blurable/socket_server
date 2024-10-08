import pytest
from unittest.mock import patch, MagicMock
from socket_chat.server import ClientHandler
from socket_chat.tsdict import ThreadSafeDict
from socket_chat.connection import Connection
from queue import Queue


@pytest.fixture
def mock_client_handler():
    buffer_queue = Queue()
    send_queue = Queue()

    mocked_connections = [MagicMock(), MagicMock()]
    tsdict = ThreadSafeDict()

    buffer = b''
    def recv_side_effect(bufsize):
        nonlocal buffer_queue
        nonlocal buffer
        if not bufsize and buffer_queue.empty():
            raise ValueError
        if not bufsize:
            return b''
        if not buffer:
            buffer = buffer_queue.get()

        chunk = buffer[ : bufsize]
        buffer = buffer[bufsize : ]
        return chunk 

    def send_side_effect(data):
        send_queue.put(data)   

    for mocked_connection in mocked_connections:
        mocked_connection.recv.side_effect = recv_side_effect
        mocked_connection.send.side_effect = send_side_effect
    
    tsdict.add_if_not_exists('Username', mocked_connections[0])
    
    client = ClientHandler(mocked_connections[1], tsdict)
    yield client, buffer_queue, send_queue

    

