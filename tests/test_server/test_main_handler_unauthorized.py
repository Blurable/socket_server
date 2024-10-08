import pytest
import socket_chat.protocol as protocol


def handler_error_tests():
    pkt1 = b'1239321312'

    pkt2 = protocol.chat_command()
    pkt2.comm_type = pkt2.COMM_TYPE.COMM_MEMBERS.value

    pkt3 = protocol.chat_connack()
    pkt3.conn_type = pkt3.CONN_TYPE.CONN_RETRY.value

    pkt4 = protocol.chat_disconnect()

    pkt5 = protocol.chat_msg()

    return [pkt1, pkt2.pack(), pkt3.pack(), pkt4.pack(), pkt5.pack()]



@pytest.mark.parametrize('recv', handler_error_tests())
def test_main_handler_unauthorized(mock_client_handler, recv):
    client, buffer_queue, _ = mock_client_handler
    buffer_queue.put(recv)
    with pytest.raises(ValueError):
        client.main_handler()


