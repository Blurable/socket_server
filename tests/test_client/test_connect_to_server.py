import pytest
import asyncio
from unittest.mock import patch, MagicMock


async def error(*args):
    raise ValueError

async def fake_connection(*args):
    return MagicMock(), MagicMock()


@pytest.mark.asyncio
async def test_connect_to_server_error(mock_client):
    client, _, _, _ = mock_client
    with patch.object(asyncio, 'open_connection', side_effect=error):
        await client.connect_to_server()

@pytest.mark.asyncio
async def test_connect_to_server_success(mock_client):
    client, _, _, _ = mock_client
    client.connection = None
    with patch.object(asyncio, 'open_connection', side_effect=fake_connection):
        await client.connect_to_server()

    assert client.connection is not None
