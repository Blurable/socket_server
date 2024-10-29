import pytest
import socket_chat.protocol as protocol
from socket_chat.tsdict import ThreadSafeDict


@pytest.mark.parametrize('clients_in_dict', [(True), (False)])
def test_main_handler_msg_broadcast(mock_client_handler, clients_in_dict):
    client, buffer_queue, send_queue = mock_client_handler

    if not clients_in_dict:
        client.clients = ThreadSafeDict()
    client.username = 'Artyom'
    client.clients.add_if_not_exists(client.username, client.client)
    rcv_msg = protocol.chat_msg()
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

    snd_msg = protocol.chat_msg()
    snd_msg.msg = ''
    snd_msg.dst = ''
    snd_msg.src = ''

    if not clients_in_dict:
        assert send_queue.empty()
    else:
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

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

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
    rcv_msg.dst = 'Dummy'
    rcv_msg.msg = 'Hello'
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

    snd_msg = protocol.chat_msg()
    snd_msg.msg = 'Hello'
    snd_msg.dst = 'Dummy'
    snd_msg.src = client.username

    packed_msg = send_queue.get()

    assert packed_msg == snd_msg.pack()


def test_msg_error_with_dst(mock_client_handler):
    client, buffer_queue, send_queue = mock_client_handler

    client.username = 'Artyom'
    test_client = 'Fake'
    client.clients.add_if_not_exists(test_client, 'fake_socket')

    rcv_msg = protocol.chat_msg()
    rcv_msg.src = client.username
    rcv_msg.dst = test_client
    rcv_msg.msg = f'Hello {test_client}'
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

    snd_msg = protocol.chat_msg()
    snd_msg.msg = f'{test_client} is offline'
    snd_msg.dst = client.username
    snd_msg.src = protocol.SERVER_CONFIG.SERVER_NAME

    packed_msg = send_queue.get()

    assert packed_msg == snd_msg.pack()


def test_broadcast_with_error(mock_client_handler):
    client, buffer_queue, send_queue = mock_client_handler

    client.username = 'Artyom'
    client.clients = ThreadSafeDict()
    client.clients.add_if_not_exists('Dummy', 'fake_socket')
    rcv_msg = protocol.chat_msg()
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

    assert send_queue.empty()
    
