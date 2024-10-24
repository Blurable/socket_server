import pytest
import socket_chat.protocol as protocol


def test_shutdown(mock_client_handler):
    client, buffer_queue, _ = mock_client_handler

    rcv_msg = protocol.chat_connect()
    rcv_msg.username = 'Artyom'
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

    assert client.username in client.clients

    client.shutdown()

    assert client.username not in client.clients