import pytest
import socket_chat.protocol as protocol
from unittest.mock import patch, AsyncMock


def get_test_handler_msg_data(): 
    client_username = 'Test_User'
    broadcast_clients = ('Fake_User1', 'Fake_User2')
    dm_client = 'Dm_User'
    not_client = 'Not_Client'
    cases = []

    msg = protocol.chat_msg()
    msg.msg = 'Hello'
    msg.src = client_username

    reply = protocol.chat_msg()
    reply.src = protocol.SERVER_CONFIG.SERVER_NAME
    reply.dst = client_username
    reply.msg = f'{not_client} is offline'

    msg.dst = ''
    cases.append((msg.pack(), client_username, broadcast_clients, msg.pack()))

    msg.dst = dm_client
    cases.append((msg.pack(), client_username, (dm_client,), msg.pack()))

    msg.dst = not_client
    cases.append((msg.pack(), client_username, (), reply.pack()))

    return cases


@pytest.mark.parametrize('pkt, client_username, fake_clients_usernames, expected_msg', get_test_handler_msg_data())
@pytest.mark.asyncio
async def test_handler_msg(fake_recv, pkt, client_username, fake_clients_usernames, expected_msg, client_handler_fixture):
    mocked_client = client_handler_fixture.client
    client_handler_fixture.username = client_username
    hdr, payload = fake_recv

    for client in fake_clients_usernames:
        client_handler_fixture.clients[client] = AsyncMock()

    await client_handler_fixture.handle_pkt(hdr, payload)

    if not client_handler_fixture.clients:
        mocked_client.send.assert_awaited_once_with(expected_msg)
    for mocked_client in client_handler_fixture.clients.values():
        mocked_client.send.assert_awaited_once_with(expected_msg)


@pytest.mark.parametrize('dst', [('disconnected_error'), ('not_client_error'), ('broadcast_error')])
@pytest.mark.asyncio
async def test_handler_msg_errors(dst, client_handler_fixture):
    async def fake_send(*args):
        raise Exception
    
    client_handler_fixture.client.send.side_effect = fake_send
    fake_client = AsyncMock()
    fake_client.send.side_effect = fake_send

    fake_client_username = 'Fake_Client'
    msg = protocol.chat_msg()
    match dst:
        case 'disconnected_error':
            client_handler_fixture.clients[fake_client_username] = fake_client
            msg.dst = fake_client_username
        case 'not_client_error':
            msg.dst = fake_client_username
        case 'broadcast_error':
            client_handler_fixture.clients[fake_client_username] = fake_client
            msg.dst = ''


    try:
        await client_handler_fixture.handle_msg(msg)
    except:
        assert True