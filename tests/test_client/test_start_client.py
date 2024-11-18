import pytest
from unittest.mock import patch, AsyncMock
import asyncio


async def func_mock(*args):
    return None

async def fake_receiver(*args):
    await asyncio.sleep(2)

async def fake_sender(*args):
    await asyncio.sleep(5)

async def error(*args):
    raise ValueError


@pytest.mark.asyncio
async def test_start_client(mock_client):
    client, _, _, _ = mock_client
    try:
        with patch.object(client, 'connect_to_server', side_effect=func_mock), \
            patch.object(client, 'authorize', side_effect=func_mock), \
            patch.object(client, 'receiver', side_effect=fake_receiver), \
            patch.object(client, 'sender', side_effect=fake_sender):
            await client.start_client()
    except:
        assert False


@pytest.mark.asyncio
async def test_start_client_error(mock_client):
    client, _, _, _ = mock_client

    try:
        with patch.object(client, 'connect_to_server', side_effect=func_mock), \
            patch.object(client, 'authorize', side_effect=error):
            await client.start_client()
    except:
        assert False
    client.connection.close.assert_awaited_once()
