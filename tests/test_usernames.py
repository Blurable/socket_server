import pytest
import socket_chat.connection as connection
import socket_chat.protocol as protocol
import socket

@pytest.mark.parametrize("username, expected_result", [
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
def test_client_usernames(clients_dict, username, expected_result):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((socket.gethostbyname(socket.gethostname()), 54321))
    conn = connection.Connection(client_socket)

    pkt = protocol.chat_connect()
    pkt.username = username
    conn.send(pkt.pack())

    hdr_bytes = conn.recv(protocol.chat_header.PKT_TYPE_FIELD_SIZE + 
                          protocol.chat_header.PKT_LEN_FIELD_SIZE)
    hdr = protocol.chat_header()
    hdr.unpack(hdr_bytes)

    payload = conn.recv(hdr.msg_len)
    if len(payload) != hdr.msg_len:
        raise ValueError
    assert hdr.msg_type == protocol.MSG_TYPE.CHAT_CONNACK
    pkt = protocol.chat_connack()
    pkt.unpack(payload)
    if expected_result == False:
        assert pkt.conn_type == protocol.chat_connack.CONN_TYPE.CONN_RETRY
        return
    assert pkt.conn_type == protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED
    assert (username in clients_dict) == expected_result
    
