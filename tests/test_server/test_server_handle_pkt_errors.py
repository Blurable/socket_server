import pytest
import socket_chat.protocol as protocol
from unittest.mock import patch


def get_handle_pkt_data():
    username = 'Test_User'
    connack = protocol.chat_connack()
    connack.conn_type = connack.CONN_TYPE.CONN_ACCEPTED.value


    return [(connack.pack(), None, ValueError), (connack.pack(), username, protocol.WrongProtocolTypeError)]


@pytest.mark.parametrize('pkt, username, error', get_handle_pkt_data())
@pytest.mark.asyncio
async def test_handle_pkt_errors(fake_recv, pkt, username, error, client_handler_fixture):
    hdr, payload = fake_recv

    if username:
        client_handler_fixture.username = username
    
    with pytest.raises(error):
        await client_handler_fixture.handle_pkt(hdr, payload)