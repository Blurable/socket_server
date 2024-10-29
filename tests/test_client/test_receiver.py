import pytest
import socket_chat.protocol as protocol
import time


def test_client_receiver(mock_client):
    client, buffer_queue, _, _ = mock_client

    msg = protocol.chat_msg()
    msg.src = 'Art'
    msg.dst = 'Tra'
    msg.msg = 'Hello'
    buffer_queue.put(msg.pack())
    client.receiver()