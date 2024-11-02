import pytest
import socket_chat.protocol as protocol


def get_test_data():
    pkt1 = protocol.chat_command()
    pkt1.comm_type = protocol.chat_command.COMM_TYPE.COMM_MEMBERS.value

    pkt2 = protocol.chat_header()
    pkt2.msg_type = protocol.MSG_TYPE.CHAT_CONNACK.value

    pkt3 = protocol.chat_disconnect()

    pkt4 = b'\x99\x01\x00\x99'

    return [(pkt1.pack()), (pkt2.pack()), (pkt3.pack()), (pkt4)]


@pytest.mark.parametrize('recv', get_test_data())
def test_authorization_wrong_type(mock_client, recv):
    client, recv_queue, input_queue, _ = mock_client

    input_queue.put('Baho')
    recv_queue.put(recv)
    with pytest.raises(protocol.WrongProtocolTypeError):
        client.authorize()

    
def test_authorization_wrong_protocol_version(mock_client):
    client, recv_queue, input_queue, _ = mock_client

    input_queue.put('Baho')

    pkt = protocol.chat_connack()
    pkt.conn_type = protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value
    recv_queue.put(pkt.pack())

    with pytest.raises(protocol.WrongProtocolVersionError):
        client.authorize()