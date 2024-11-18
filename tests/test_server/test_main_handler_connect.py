import pytest
import socket_chat.protocol as protocol
from unittest.mock import patch, AsyncMock


def get_test_handler_connect_data():
    connect = protocol.chat_connect()
    connack = protocol.chat_connack()
    cases = []

    connect.username = 'Connect'
    connack.conn_type = connack.CONN_TYPE.CONN_ACCEPTED.value
    cases.append((connect.pack(), connack.pack(), connect.username))

    connect.username = 'Retry'
    connack.conn_type = connack.CONN_TYPE.CONN_RETRY.value
    cases.append((connect.pack(), connack.pack(), connect.username))

    connect.username = 'Error'
    connect.protocol_version = ''
    connack.conn_type = connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value
    cases.append((connect.pack(), connack.pack(), connect.username))

    return cases


@pytest.mark.parametrize('pkt, expected_send_pkt, username', get_test_handler_connect_data())
@pytest.mark.asyncio
async def test_handler_connect(fake_recv, pkt, expected_send_pkt, username, client_handler_fixture):
    mocked_client = client_handler_fixture.client
    hdr, payload = fake_recv

    if username == 'Retry':
        client_handler_fixture.clients['Retry'] = AsyncMock()
    try:
        await client_handler_fixture.handle_pkt(hdr, payload)
    except protocol.WrongProtocolVersionError:
        assert True

    mocked_client.send.assert_awaited_once_with(expected_send_pkt)
    if username == 'Connect':
        assert username in client_handler_fixture.clients