import pytest
import socket_chat.protocol as protocol


def test_authorization_retry(mock_client):
    client, recv_queue, input_queue = mock_client

    input_queue.put('Baho')
    pkt1 = protocol.chat_connack()
    pkt1.conn_type = protocol.chat_connack.CONN_TYPE.CONN_RETRY
    recv_queue.put(pkt1.pack())

    input_queue.put('Artyom')
    pkt2 = protocol.chat_connack()
    pkt2.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED
    recv_queue.put(pkt2.pack())
    
    client.authorize()

    assert client.username == 'Artyom'