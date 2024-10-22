import pytest
import socket_chat.protocol as protocol


def test_main_handler_disconnect(mock_client_handler):
    client, buffer_queue, send_queue = mock_client_handler
    
    client.username = 'Artyom'
    client.clients.add_if_not_exists(client.username, client.client)

    rcv_msg = protocol.chat_disconnect()
    buffer_queue.put(rcv_msg.pack())

    client.run()

    snd_msg = protocol.chat_msg()
    snd_msg.src = protocol.SERVER_CONFIG.SERVER_NAME
    snd_msg.dst = ''
    snd_msg.msg = f'{client.username} disconnected'

    assert snd_msg.pack() == send_queue.get()
    assert client.username not in client.clients