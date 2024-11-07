import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_start_server(server_fixture):
    server = server_fixture
    with patch('asyncio.start_server') as start_server_mock:
        start_server_mock.return_value = AsyncMock()
        await server.start_server()
        start_server_mock.assert_called_once_with(server.client_handler, server.host_ip, server.host_port)


@pytest.mark.asyncio
async def test_start_server_error(server_fixture):
    server = server_fixture
    def fake_error(*args):
        raise ValueError
    with patch('asyncio.start_server', side_effect=fake_error):
        with pytest.raises(ValueError):
            await server.start_server()