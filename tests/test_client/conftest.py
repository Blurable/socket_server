import pytest
from unittest.mock import patch, MagicMock
from socket_chat.client import Client
from queue import Queue



@pytest.fixture
def mock_client():
    buffer_queue = Queue()
    input_queue = Queue()
    send_queue = Queue()

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

    def mock_sendall(data):
        nonlocal send_queue
        return send_queue.put(data)
    
    mock_socket.recv.side_effect = recv_side_effect
    mock_socket.send.side_effect = mock_sendall   
    with patch('builtins.input', side_effect=lambda prompt: input_queue.get()):
        client = Client(server_port=54321)
        client.server = mock_socket

        yield client, buffer_queue, input_queue, send_queue
