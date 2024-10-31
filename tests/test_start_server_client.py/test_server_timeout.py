import pytest
import socket
import socket_chat.protocol as protocol
import time
import errno


@pytest.mark.parametrize('recv_val', [(b'\x01'), (b'111'), (b'0')])
def test_timeout(test_server, recv_val):
    server, add_q, del_q, exceptions = test_server

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server.addr)


    username = 'Art'
    connect = protocol.chat_connect()
    connect.username = username
    client.send(connect.pack())

    assert add_q.get() == username
    assert username in server.clients.dictionary

    client.send(recv_val)
    time.sleep(6)

    assert del_q.get() == username
    assert username not in server.clients.dictionary

    server.server_socket.close()
    assert exceptions.get() == socket.errno.WSAENOTSOCK

