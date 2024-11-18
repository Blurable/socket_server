import pytest
from unittest.mock import patch
import asyncio


@pytest.mark.asyncio
async def test_recv(connection):
    text = 'Test'
    async def fake_read(*args):
        return text
    len = 5
    with patch.object(connection.reader, 'read', side_effect=fake_read) as mock_read:
        msg = await connection.recv(len)
    mock_read.assert_awaited_once_with(len)
    assert msg == text



@pytest.mark.asyncio
async def test_recv_reset_error(connection):
    len = 5
    async def fake_read(*args):
        return None
    
    with patch.object(connection.reader, 'read', side_effect=fake_read) as mock_read:
        with pytest.raises(ConnectionResetError):
            await connection.recv(len)
    mock_read.assert_awaited_once_with(len)


@pytest.mark.asyncio
async def test_recv_timeout_error(connection):
    from socket_chat.connection import ConnectionTimedOutError
    len = 5
    wait_time = 2

    async def fake_read(*args):
        await asyncio.sleep(wait_time+1)

    with patch.object(connection.reader, 'read', side_effect=fake_read) as mock_read:
        with pytest.raises(ConnectionTimedOutError):
            await connection.recv(len, wait_time)
    mock_read.assert_awaited_once_with(len)


@pytest.mark.asyncio
async def test_recv_error(connection):
    len = 5

    async def fake_read(*args):
        raise ValueError
    with patch.object(connection.reader, 'read', side_effect=fake_read) as mock_read:
        with pytest.raises(ConnectionResetError):
            await connection.recv(len)
    mock_read.assert_awaited_once_with(len)