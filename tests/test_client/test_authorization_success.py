import pytest
import socket_chat.protocol as protocol


def test_authorization_success(mock_client):
    client, recv_queue, input_queue, send_queue = mock_client

    input_queue.put('Artyom')
    
    pkt = protocol.chat_connack()
    pkt.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value
    recv_queue.put(pkt.pack())
    client.authorize()
    
    connect = protocol.chat_connect()
    connect.username = 'Artyom'
    assert send_queue.get() == connect.pack()
    assert client.username == 'Artyom'
