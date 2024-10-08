import pytest
import socket_chat.protocol as protocol


def test_handle_success(mock_client):
    client, recv_queue, _, _ = mock_client

    rcv_msg = protocol.chat_msg()
    recv_queue.put(rcv_msg.pack())
    hdr, payload = client.recv_pkt()
    assert hdr.msg_type == protocol.MSG_TYPE.CHAT_MSG.value
    try:
        client.handle(hdr, payload)
    except:
        assert False
