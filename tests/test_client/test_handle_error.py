import pytest
import socket_chat.protocol as protocol


def get_test_data():
    pkt1 = protocol.chat_command()
    pkt1.comm_type = protocol.chat_command.COMM_TYPE.COMM_MEMBERS.value

    pkt2 = protocol.chat_header()
    pkt2.msg_type = protocol.MSG_TYPE.CHAT_CONNACK.value

    pkt3 = b'30120329412'

    pkt4 = protocol.chat_disconnect()
    
    pkt5 = protocol.chat_connect()
    pkt5.username = 'Baho'

    return [(pkt1.pack()), (pkt2.pack()), (pkt3), (pkt4.pack()), (pkt5.pack())]

@pytest.mark.parametrize('recv', get_test_data())
@pytest.mark.asyncio
async def test_handle_error(mock_client, recv):
    client, recv_queue, _, _ = mock_client
    
    await recv_queue.put(recv)
    with pytest.raises(protocol.WrongProtocolTypeError):
        hdr, payload = await client.recv_pkt()
        await client.handle(hdr, payload)
