import pytest
from unittest.mock import patch, MagicMock
from socket_chat.client import Client
from queue import Queue
import time



@pytest.fixture
def mock_client():
    buffer_queue = Queue()
    input_queue = Queue()
    send_queue = Queue()
    timeout = None

    mock_socket = MagicMock()

    buffer = b''
    def recv_side_effect(bufsize):
        nonlocal buffer_queue, buffer

        if not bufsize and buffer_queue.empty():
            raise ValueError
        if not bufsize:
            return b''
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

    def mock_sendall(data):
        nonlocal send_queue
        return send_queue.put(data)
    
    def mock_input(prompt):
        msg = input_queue.get()
        if isinstance(msg, Exception):
            raise msg
        return msg
       
    def mock_settimeout(time):
        nonlocal timeout
        timeout = time
        
    mock_socket.recv.side_effect = recv_side_effect
    mock_socket.send.side_effect = mock_sendall
    mock_socket.settimeout.side_effect = mock_settimeout
    with patch('builtins.input', side_effect=mock_input):
        client = Client(server_port=54321)
        client.server = mock_socket

        yield client, buffer_queue, input_queue, send_queue