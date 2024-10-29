import pytest
import socket_chat.protocol as protocol


def handler_error_tests():
    pkt1 = protocol.chat_command()
    pkt1.comm_type = pkt1.COMM_TYPE.COMM_MEMBERS.value

    pkt2 = protocol.chat_connack()
    pkt2.conn_type = pkt2.CONN_TYPE.CONN_RETRY.value

    pkt3 = protocol.chat_disconnect()

    pkt4 = protocol.chat_msg()

    return [pkt1.pack(), pkt2.pack(), pkt3.pack(), pkt4.pack()]



@pytest.mark.parametrize('recv', handler_error_tests())
def test_main_handler_unauthorized(mock_client_handler, recv):
    client, buffer_queue, _ = mock_client_handler
    buffer_queue.put(recv)
    with pytest.raises(ValueError):
        hdr, payload = client.recv_pkt()
        client.handle_pkt(hdr, payload)


