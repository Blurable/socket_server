import pytest
import socket
from socket_chat.connection import Connection
import socket_chat.protocol as protocol
import threading


login_barrier = threading.Barrier(2)
msg_barrier = threading.Barrier(3)

def client_connection(username):

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((socket.gethostbyname(socket.gethostname()), 54321))
    cl_conn = Connection(client_socket)

    conn = protocol.chat_connect()
    conn.username = username
    cl_conn.send(conn.pack())

    hdr_bytes = cl_conn.recv(protocol.chat_header.PKT_TYPE_FIELD_SIZE + 
                            protocol.chat_header.PKT_LEN_FIELD_SIZE)
    hdr = protocol.chat_header()
    hdr.unpack(hdr_bytes)
    cl_conn.recv(hdr.msg_len)

    login_barrier.wait()

    msg = protocol.chat_msg()
    msg.src = username
    msg.dst = 'Baho'
    msg.msg = 'Hello'
    cl_conn.send(msg.pack())
    

def test_dms():
    threading.Thread(target=client_connection, args=('Artyom',), daemon=True).start()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((socket.gethostbyname(socket.gethostname()), 54321))
    cl_conn = Connection(client_socket)

    conn = protocol.chat_connect()
    conn.username = 'Baho'
    cl_conn.send(conn.pack())

    hdr_bytes = cl_conn.recv(protocol.chat_header.PKT_TYPE_FIELD_SIZE + 
                            protocol.chat_header.PKT_LEN_FIELD_SIZE)
    hdr = protocol.chat_header()
    hdr.unpack(hdr_bytes)
    cl_conn.recv(hdr.msg_len)

    login_barrier.wait()

    hdr_bytes = cl_conn.recv(protocol.chat_header.PKT_TYPE_FIELD_SIZE + 
                            protocol.chat_header.PKT_LEN_FIELD_SIZE)
    hdr = protocol.chat_header()
    hdr.unpack(hdr_bytes)
    payload = cl_conn.recv(hdr.msg_len)

    msg = protocol.chat_msg()
    msg.unpack(payload)

    assert msg.src == 'Artyom'
    assert msg.dst == 'Baho'
    assert msg.msg == 'Hello'