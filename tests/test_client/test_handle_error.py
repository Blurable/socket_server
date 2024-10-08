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

    return [(pkt1.pack()), (pkt2.pack()), (pkt3), (pkt4.pack()), (pkt5.pack())]

@pytest.mark.parametrize('recv', get_test_data())
def test_handle_error(mock_client, recv):
    client, recv_queue, _, _ = mock_client
    
    recv_queue.put(recv)
    with pytest.raises(ValueError):
        hdr, payload = client.recv_pkt()
        client.handle(hdr, payload)
