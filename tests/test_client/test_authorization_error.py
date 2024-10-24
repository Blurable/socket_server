import pytest
import socket_chat.protocol as protocol


def get_test_data():
    pkt1 = protocol.chat_command()
    pkt1.comm_type = protocol.chat_command.COMM_TYPE.COMM_MEMBERS.value

    pkt2 = protocol.chat_header()
    pkt2.msg_type = protocol.MSG_TYPE.CHAT_CONNACK.value

    pkt3 = b'\x03\x99\x0094122'

    pkt4 = protocol.chat_disconnect()

    pkt5 = b'\x99\x01\x00\x99'

    return [(pkt1.pack()), (pkt2.pack()), (pkt3), (pkt4.pack()), (pkt5)]


@pytest.mark.parametrize('recv', get_test_data())
def test_authorization_error(mock_client, recv):
    client, recv_queue, input_queue, _ = mock_client

    input_queue.put('Baho')
    recv_queue.put(recv)
    with pytest.raises(ValueError):
        client.authorize()