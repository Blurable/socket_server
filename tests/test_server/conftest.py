import pytest
import socket
from unittest.mock import patch, MagicMock
from socket_chat.server import Server
from socket_chat.connection import Connection


@pytest.fixture
def server_fixture():
    host_ip = socket.gethostbyname(socket.gethostname())
    host_port = 54321
    with patch('socket_chat.server.logging.getLogger') as mock_logger:
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        server = Server(host_port)
        assert server.host_port == host_port
        assert server.host_ip == host_ip
        assert server.addr == (host_ip, host_port)
        assert server.clients == {}
        assert server.server is None
        yield server
