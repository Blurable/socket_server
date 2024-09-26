import pytest
import socket
from socket_chat.connection import Connection
import socket_chat.protocol as protocol
import threading


login_barrier = threading.Barrier(2)
msg_barrier = threading.Barrier(3)
msg = ''

def client_connection(username):
    global msg

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

    comm = protocol.chat_command()
    comm.comm_type = protocol.chat_command.COMM_TYPE.COMM_MEMBERS
    cl_conn.send(comm.pack())


    hdr_bytes = cl_conn.recv(protocol.chat_header.PKT_TYPE_FIELD_SIZE + 
                             protocol.chat_header.PKT_LEN_FIELD_SIZE)
    hdr = protocol.chat_header()
    hdr.unpack(hdr_bytes)
    payload = cl_conn.recv(hdr.msg_len)
    pkt = protocol.chat_msg()
    pkt.unpack(payload)
    msg = pkt.msg
    msg_barrier.wait()

    



def test_dms():
    global msg

    threading.Thread(target=client_connection, args=('Artyom',), daemon=True).start()
    threading.Thread(target=client_connection, args=('Baho',), daemon=True).start()
    msg_barrier.wait()

    assert msg == 'Artyom\nBaho' or msg == 'Baho\nArtyom'