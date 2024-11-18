import pytest
import socket
from unittest.mock import patch, MagicMock, AsyncMock
from socket_chat.server import Server, ClientHandler
import socket_chat.protocol as protocol


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


@pytest.fixture
def mock_client():
    client = AsyncMock()
    client.is_active = True
    return client


@pytest.fixture
def clients_dict():
    return {}


@pytest.fixture
def client_handler_fixture(mock_client, clients_dict):
    with patch('socket_chat.server.logging.getLogger') as mock_logger:
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance
        client_handler = ClientHandler(mock_client, clients_dict)
        assert client_handler.client == mock_client
        assert client_handler.clients == clients_dict
        yield client_handler


@pytest.fixture
def fake_recv(pkt):
    hdr_bytes = pkt[:protocol.chat_header.PKT_TYPE_FIELD_SIZE + protocol.chat_header.PKT_LEN_FIELD_SIZE]
    hdr = protocol.chat_header()
    hdr.unpack(hdr_bytes)

    payload_len = hdr.msg_len
    payload = b''
    while len(payload) < payload_len:
        payload = pkt[len(hdr_bytes):len(hdr_bytes)+hdr.msg_len]
    return hdr, payload

