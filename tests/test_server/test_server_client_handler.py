import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.asyncio
async def test_client_handler(server_fixture):
    server = server_fixture
    client_reader = MagicMock()
    client_writer = MagicMock()

    def new_run():
        raise ValueError

    with patch('socket_chat.server.ClientHandler.run', side_effect=new_run):
        try:
            await server.client_handler(client_reader, client_writer)
        except:
            assert False