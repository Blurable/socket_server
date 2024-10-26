import pytest
from unittest.mock import patch
import socket
import time

from socket_chat.server import Server, ClientHandler
import threading


def test_server_start_errors():
    server1 = Server(54321)
    threading.Thread(target=server1.start_server, daemon=True).start()
    server2 = Server(54321)
    th = threading.Thread(target=server2.start_server, daemon=True)
    th.start()
    th.join()

    assert server2.is_active == False
    server1.server_socket.close()


def test_server_accept_errors(test_server):
    server, _, _ = test_server
    server.server_socket.close()
    time.sleep(1)
    assert server.is_active == False


@pytest.mark.parametrize('error, expected_res', [(Exception, True), (socket.error, True)])
def test_patched_accept_errors(error, expected_res, test_client):
    def new_start():
        raise error
    
    server = Server(54321)
    original_start = threading.Thread.start
    with patch.object(threading.Thread, 'start', side_effect=new_start):
        original_start(threading.Thread(target=server.start_server, daemon=True))
        time.sleep(1)
        assert server.is_active == expected_res

    server.server_socket.close()