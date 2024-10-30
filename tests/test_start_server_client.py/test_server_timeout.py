import pytest
import socket
import socket_chat.protocol as protocol
import time


@pytest.mark.parametrize('recv_val', [(b'\x01'), (b'111'), (b'0')])
def test_timeout(test_server, recv_val):
    server, add_q, del_q, _ = test_server

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server.addr)


    username = 'Art'
    connect = protocol.chat_connect()
    connect.username = username
    client.send(connect.pack())

    assert add_q.get() == username
    assert server.clients.get_if_exists(username) != None

    client.send(recv_val)
    time.sleep(6)
    assert del_q.get() == username
    assert server.clients.get_if_exists(username) == None

    server.server_socket.close()

