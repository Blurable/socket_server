import pytest
import socket_chat.protocol as protocol
from unittest.mock import patch, AsyncMock


def get_test_handler_command_data():
    command = protocol.chat_command()
    command.comm_type = command.COMM_TYPE.COMM_MEMBERS.value
    msg = protocol.chat_msg()
    client_username = 'Test_User'
    fake_clients = ('Fake_User1', 'Fake_User2')  
    cases = []

    msg.msg = "You are alone in the chat"
    msg.src = protocol.SERVER_CONFIG.SERVER_NAME
    msg.dst = client_username
    cases.append((command.pack(), client_username, None, msg.pack()))

    msg.msg = "Fake_User1\nFake_User2"
    cases.append((command.pack(), client_username, fake_clients, msg.pack()))

    return cases


@pytest.mark.parametrize('pkt, client_username, fake_clients, expected_msg', get_test_handler_command_data())
@pytest.mark.asyncio
async def test_handler_command(fake_recv, pkt, client_username, fake_clients, expected_msg, client_handler_fixture):
    mocked_client = client_handler_fixture.client
    client_handler_fixture.username = client_username
    hdr, payload = fake_recv

    if fake_clients:
        for client in fake_clients:
            client_handler_fixture.clients[client] = AsyncMock()

    await client_handler_fixture.handle_pkt(hdr, payload)

    mocked_client.send.assert_awaited_once_with(expected_msg)


@pytest.mark.asyncio
async def test_handler_command_error(client_handler_fixture):
    command_pkt = protocol.chat_command()
    command_pkt.comm_type = 'Error'
    with pytest.raises(protocol.WrongProtocolTypeError):
        await client_handler_fixture.handle_command(command_pkt)