import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from socket_chat.connection import Connection

   
@pytest.mark.asyncio
async def test_send(connection):
    con = connection
    msg = b'test'
    con.writer = MagicMock()
    def fake_write(*args):
        nonlocal con
        con.writer = AsyncMock()
    
    with patch.object(con.writer, 'write', side_effect=fake_write) as mocked_write:
        await con.send(msg)

        mocked_write.assert_called_once_with(msg)
        con.writer.drain.assert_awaited_once()