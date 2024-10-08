import pytest
import socket_chat.protocol as protocol


def get_test_data():
    return [('Artyom', protocol.SERVER_CONFIG.CURRENT_VERSION, protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED),
            ('Username', protocol.SERVER_CONFIG.CURRENT_VERSION, protocol.chat_connack.CONN_TYPE.CONN_RETRY),
            ('Artyom', '', protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION)]


@pytest.mark.parametrize('username, protocol_version, conn_type', get_test_data())
def test_main_handler_connect(mock_client_handler, username, protocol_version, conn_type):
    client, buffer_queue, send_queue = mock_client_handler

    rcv_msg = protocol.chat_connect()
    rcv_msg.username = username
    rcv_msg.protocol_version = protocol_version
    buffer_queue.put(rcv_msg.pack())

    client.main_handler()

    snd_msg = protocol.chat_connack()
    snd_msg.conn_type = conn_type

    assert snd_msg.pack() == send_queue.get()
    if conn_type == protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED:
        assert username in client.clients
        assert client.clients[username] == client.client
    elif conn_type == protocol.chat_connack.CONN_TYPE.CONN_RETRY:
        assert username in client.clients
    elif conn_type == protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION:
        assert username not in client.clients


