import pytest
from unittest.mock import patch, MagicMock
from socket_chat.server import ClientHandler
from socket_chat.tsdict import ThreadSafeDict
import socket
import time
from queue import Queue


@pytest.fixture
def mock_client_handler():
    buffer_queue = Queue()
    send_queue = Queue()
    timeout = 0

    mocked_connections = [MagicMock(), MagicMock()]
    tsdict = ThreadSafeDict()

    buffer = b''
    def recv_side_effect(bufsize):
        nonlocal buffer_queue
        nonlocal buffer
        if bufsize and not buffer and buffer_queue.empty():
            raise socket.error
        if not bufsize and buffer_queue.empty():
            raise ValueError
        if not buffer:
            if not buffer_queue.empty():
                buffer = buffer_queue.get()
            else:
                time.sleep(timeout)
                if buffer_queue.empty():
                    raise ValueError
                else:
                    buffer = buffer_queue.get()

        chunk = buffer[ : bufsize]
        buffer = buffer[bufsize : ]
        return chunk 

    def send_side_effect(data):
        send_queue.put(data)

    def settimeout_side_effect(time):
        nonlocal timeout
        timeout = time

    for mocked_connection in mocked_connections:
        mocked_connection.recv.side_effect = recv_side_effect
        mocked_connection.send.side_effect = send_side_effect
        mocked_connection.settimeout.side_effect = settimeout_side_effect
    
    tsdict.add_if_not_exists('Username', mocked_connections[0])
    
    client = ClientHandler(mocked_connections[1], tsdict)
    yield client, buffer_queue, send_queue