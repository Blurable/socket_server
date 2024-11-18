import pytest
from socket_chat.connection import Connection
from unittest.mock import patch, AsyncMock, MagicMock
import asyncio


@pytest.fixture
def connection():
    writer = AsyncMock()
    reader = AsyncMock()
    mock_logger = MagicMock()
    with patch('socket_chat.connection.logging.getLogger', return_value=mock_logger):
        con = Connection(writer, reader)
        con.logger = mock_logger
        return con