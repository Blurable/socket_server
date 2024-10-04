import pytest
import socket
from unittest.mock import patch, MagicMock
from socket_chat.client import Client
from socket_chat.connection import Connection
from queue import Queue
import threading


@pytest.fixture
def mock_client():
    buffer_queue = Queue()
    input_queue = Queue()

    mock_socket = MagicMock()

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

    mock_socket.recv.side_effect = recv_side_effect
    
    with patch('socket.socket', return_value=mock_socket):
        client = Client(server_port=54321)
        client.server = mock_socket

        with patch('builtins.input', side_effect=lambda prompt: input_queue.get()):
            yield client, buffer_queue, input_queue
