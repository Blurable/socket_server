import pytest
import socket_chat.protocol as protocol


def get_test_data():
    return [
            ('Artyom', protocol.SERVER_CONFIG.CURRENT_VERSION, protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value),
            ('Dummy', protocol.SERVER_CONFIG.CURRENT_VERSION, protocol.chat_connack.CONN_TYPE.CONN_RETRY.value),
            ('Artyom', '', protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value)
            ]


@pytest.mark.parametrize('username, protocol_version, conn_type', get_test_data())
def test_main_handler_connect(mock_client_handler, username, protocol_version, conn_type):
    client, buffer_queue, send_queue = mock_client_handler

    rcv_msg = protocol.chat_connect()
    rcv_msg.username = username
    rcv_msg.protocol_version = protocol_version
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    if conn_type == protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value:
        with pytest.raises(protocol.ProtocolVersionException):
            client.handle_pkt(hdr, payload)
        assert username not in client.clients
        return
    client.handle_pkt(hdr, payload)

    snd_msg = protocol.chat_connack()
    snd_msg.conn_type = conn_type

    assert snd_msg.pack() == send_queue.get()
    if conn_type == protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value:
        assert username in client.clients
        assert client.clients.get_if_exists(username) == client.client
    elif conn_type == protocol.chat_connack.CONN_TYPE.CONN_RETRY.value:
        assert username in client.clients


