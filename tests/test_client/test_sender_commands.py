import pytest
import socket_chat.protocol as protocol


def get_test_data():
    quit_com = protocol.chat_disconnect()

    members_com = protocol.chat_command()
    members_com.comm_type = members_com.COMM_TYPE.COMM_MEMBERS.value

    msg_com = protocol.chat_msg()
    msg_com.msg = 'Hi'

    return [('/quit', quit_com), ('/members', members_com), (msg_com.msg, msg_com)]


@pytest.mark.parametrize('input, send', get_test_data())
@pytest.mark.asyncio
async def test_sender_commands(mock_client, input, send):
    client, _, input_queue, send_queue = mock_client

    await input_queue.put(input)
    await input_queue.put(ValueError())

    await client.sender()
    
    assert await send_queue.get() == send.pack()