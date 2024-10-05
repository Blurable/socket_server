import pytest
from unittest.mock import patch, MagicMock
from socket_chat.server import ClientHandler
from socket_chat.tsdict import ThreadSafeDict
from queue import Queue


@pytest.fixture
def mock_server():
    buffer_queue = Queue()
    send_queue = Queue()

    mock_socket = MagicMock()
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

    mock_socket.recv.side_effect = recv_side_effect
    mock_socket.send.side_effect = lambda data: send_queue.put(data)
    
    with patch('socket.socket', return_value=mock_socket):
        handler = ClientHandler(mock_socket, tsdict)
        yield handler, buffer_queue, send_queue
    

