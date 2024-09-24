import pytest
from unittest.mock import patch
from socket_chat.client import Client
import socket_chat.protocol as protocol



def mocked_authorize(self, username, flag_status):
    global connection_flag
    conn = protocol.chat_connect()
    conn.username = username
    self.server.send(conn.pack())

    _, payload = self.recv_pkt()
    pkt = protocol.chat_connack()
    pkt.unpack(payload)

    assert pkt.conn_type == protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED



@pytest.mark.parametrize("username, flag_status", [
    ('', False),
    ('sys', False),
    ('username', False),
    ('members', False),
    ('all', False),
    ('info', False),
    ('quit', False),
    ('Artyom', True),
    (' ', False),
    ('123asd', False),
    ('asd123', True),
    ('@!#@!$', False),
    ('asd!', False)

])
def test_client_usernames(username, flag_status):
    global connection_flag
    with patch.object(Client, 'authorize', new = lambda self: mocked_authorize(self, username, flag_status)):
        client = Client(54321)

    



        
