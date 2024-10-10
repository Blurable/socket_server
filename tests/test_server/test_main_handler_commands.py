import pytest
import socket_chat.protocol as protocol
from socket_chat.tsdict import ThreadSafeDict

@pytest.mark.parametrize('clients, msg', [(False, 'You are alone in the chat'),
                                          (True, 'Username\nArtyom')] )
def test_main_handler_members_with_users(mock_client_handler, clients, msg):
    client, buffer_queue, send_queue = mock_client_handler
    
    if not clients:
        client.clients = ThreadSafeDict()
    client.username = 'Artyom'
    client.clients.add_if_not_exists(client.username, client.client)

    rcv_msg = protocol.chat_command()
    rcv_msg.comm_type = rcv_msg.COMM_TYPE.COMM_MEMBERS.value
    buffer_queue.put(rcv_msg.pack())

    hdr, payload = client.recv_pkt()
    client.handle_pkt(hdr, payload)

    snd_msg = protocol.chat_msg()
    snd_msg.src = protocol.SERVER_CONFIG.SERVER_NAME
    snd_msg.dst = client.username
    snd_msg.msg = msg

    assert snd_msg.pack() == send_queue.get()

