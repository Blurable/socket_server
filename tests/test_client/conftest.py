import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from socket_chat.client import Client
import asyncio


@pytest.fixture
def mock_client():
    buffer_queue = asyncio.Queue()
    input_queue = asyncio.Queue()
    send_queue = asyncio.Queue()

    mock_connection = AsyncMock()
    mock_logger = MagicMock()

    buffer = b''
    async def recv_side_effect(bufsize, timeout=2):
        nonlocal buffer_queue, buffer

        if bufsize and not buffer:
            buffer += await asyncio.wait_for(buffer_queue.get(), timeout)
            
        chunk = buffer[ : bufsize]
        buffer = buffer[bufsize : ]
        return chunk    

    async def mock_sendall(data):
        nonlocal send_queue
        return await send_queue.put(data)
    
    async def mock_input(prompt):
        msg = await input_queue.get()
        if isinstance(msg, Exception):
            raise msg
        return msg
       
        
    mock_connection.recv.side_effect = recv_side_effect
    mock_connection.send.side_effect = mock_sendall

    with patch('socket_chat.client.ainput', side_effect=mock_input), \
         patch('socket_chat.client.logging.getLogger', return_value=mock_logger):
        client = Client(server_port=54321)
        client.connection = mock_connection

        yield client, buffer_queue, input_queue, send_queue