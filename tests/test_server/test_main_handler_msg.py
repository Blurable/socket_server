import pytest
from unittest.mock import MagicMock
import socket_chat.protocol as protocol


def test_main_handler_msg_broadcast(mock_client_handler):
    client, buffer_queue, send_queue = mock_client_handler

    client.username = 'Artyom'
    rcv_msg = protocol.chat_msg()
    buffer_queue.put(rcv_msg.pack())

    client.main_handler()

    snd_msg = protocol.chat_msg()
    snd_msg.msg = ''
    snd_msg.dst = ''
    snd_msg.src = ''

    packed_msg = send_queue.get()

    assert packed_msg == snd_msg.pack()



def test_main_handler_unauthorized_dst(mock_client_handler):
    client, buffer_queue, send_queue = mock_client_handler

    client.username = 'Artyom'

    rcv_msg = protocol.chat_msg()
    rcv_msg.src = client.username
    rcv_msg.dst = 'Moytra'
    rcv_msg.msg = 'Hello'
    buffer_queue.put(rcv_msg.pack())

    client.main_handler()

    snd_msg = protocol.chat_msg()
    snd_msg.msg = 'Moytra is offline'
    snd_msg.dst = client.username
    snd_msg.src = protocol.SERVER_CONFIG.SERVER_NAME

    packed_msg = send_queue.get()

    assert packed_msg == snd_msg.pack()


def test_main_handler_authorized_dst(mock_client_handler):
    client, buffer_queue, send_queue = mock_client_handler

    client.username = 'Artyom'

    rcv_msg = protocol.chat_msg()
    rcv_msg.src = client.username
    rcv_msg.dst = 'Username'
    rcv_msg.msg = 'Hello'
    buffer_queue.put(rcv_msg.pack())

    client.main_handler()

    snd_msg = protocol.chat_msg()
    snd_msg.msg = 'Hello'
    snd_msg.dst = 'Username'
    snd_msg.src = client.username

    packed_msg = send_queue.get()

    assert packed_msg == snd_msg.pack()

    
