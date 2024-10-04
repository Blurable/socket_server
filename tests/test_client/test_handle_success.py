import pytest
import socket_chat.protocol as protocol


def get_test_data():
    pkt1 = protocol.chat_msg()

    pkt2 = b'\x04\x01\x00\x01'

    return [(pkt1.pack()), (pkt2)]

@pytest.mark.parametrize('recv', get_test_data())
def test_handle_success(mock_client, recv):
    client, recv_queue, _ = mock_client
    
    pkt = protocol.chat_connack()
    pkt.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED
    recv_queue.put(recv)
    hdr, payload = client.recv_pkt()
    assert hdr.msg_type == protocol.MSG_TYPE.CHAT_MSG
    try:
        client.handle(hdr, payload)
    except:
        assert False
