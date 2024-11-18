import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock



@pytest.mark.asyncio
async def test_close(connection):
    con = connection
    con.writer = MagicMock()
    def fake_close(*args):
        nonlocal con
        con.writer = AsyncMock()
    
    with patch.object(con.writer, 'close', side_effect=fake_close) as mocked_close:
        await con.close()

        assert con.is_active == False
        mocked_close.assert_called_once()
        con.writer.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_close_error(connection):
    connection.writer = MagicMock()
    def close_error(*args):
        raise ValueError
    try:
        with patch.object(connection.writer, 'close', side_effect=close_error):
            await connection.close()
    except:
        assert False