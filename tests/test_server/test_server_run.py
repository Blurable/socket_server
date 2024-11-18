import pytest
from unittest.mock import patch
import socket_chat.protocol as protocol


async def error(*args):
    raise ValueError

async def fake_recv(*args):
    return None, None

@pytest.mark.parametrize('method_to_swap', [('recv_pkt'), ('handle_pkt')])
@pytest.mark.asyncio
async def test_run(client_handler_fixture, method_to_swap):
    if method_to_swap == 'recv_pkt':
        with patch.object(client_handler_fixture, method_to_swap, side_effect=method_to_swap):
            with pytest.raises(ValueError):
                await client_handler_fixture.run()
    else:
        with patch.object(client_handler_fixture, 'recv_pkt', side_effect=fake_recv), \
             patch.object(client_handler_fixture, method_to_swap, side_effect=error):
            with pytest.raises(ValueError):
                await client_handler_fixture.run()