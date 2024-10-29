import pytest
import socket_chat.protocol as protocol


def test_main_handler_no_case(mock_client_handler):
    client, buffer_queue, send_queue = mock_client_handler

    username = 'Artyom'
    rcv_msg = protocol.chat_connect()
    rcv_msg.username = username
    rcv_msg.protocol_version = protocol.SERVER_CONFIG.CURRENT_VERSION
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

    snd_msg = protocol.chat_connack()
    snd_msg.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value

    assert snd_msg.pack() == send_queue.get()
    assert username in client.clients
    assert client.clients.get_if_exists(username) == client.client

    hdr = protocol.chat_header()
    hdr.msg_type = None
    payload = None
    with pytest.raises(protocol.ProtocolTypeException):
        client.handle_pkt(hdr, payload)
