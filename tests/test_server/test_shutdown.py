import pytest
import socket_chat.protocol as protocol
from unittest.mock import patch


def get_disconnect_data():
    dc = protocol.chat_disconnect()
    return [(dc.pack())]


@pytest.mark.parametrize('pkt', get_disconnect_data())
@pytest.mark.asyncio
async def test_handler_msg(fake_recv, pkt, client_handler_fixture):
    hdr, payload = fake_recv
    mocked_client = client_handler_fixture.client
    client_handler_fixture.username = 'Client'
    client_handler_fixture.clients[client_handler_fixture.username] = mocked_client

    await client_handler_fixture.handle_pkt(hdr, payload)
    
    mocked_client.close.assert_awaited_once()
    assert client_handler_fixture.username not in client_handler_fixture.clients
    