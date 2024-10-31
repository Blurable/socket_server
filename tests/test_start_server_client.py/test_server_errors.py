import pytest
from unittest.mock import patch
import socket
import time
from socket_chat.server import Server
import threading
import socket
from queue import Queue


def test_server_start_errors(test_server):
    server1, _, _, exc_q = test_server
    server2 = Server(54321)
    with pytest.raises(socket.error):
        server2.start_server()

    server1.server_socket.close()
    assert exc_q.get() == socket.errno.WSAENOTSOCK


@pytest.mark.parametrize('error, expected_res', [(Exception, True), (socket.error, True)])
def test_patched_accept_errors(error, expected_res, test_client):
    class MyThread(threading.Thread):
        def __init__(self, server, exc_q):
            threading.Thread.__init__(self)
            self.server = server
            self.exc_q = exc_q
        def func(self):
            self.server.start_server()

        def run(self):
            try:
                self.func()
            except Exception as e:
                self.exc_q.put(e.errno)

    def new_start():
        raise error
    
    server = Server(54321)
    exc_q = Queue()
    original_start = threading.Thread.start
    with patch.object(threading.Thread, 'start', side_effect=new_start):
        server_thread = MyThread(server, exc_q)
        original_start(server_thread)
        time.sleep(1)
        assert server_thread.is_alive() == expected_res
    server.server_socket.close()
    assert exc_q.get() == socket.errno.WSAENOTSOCK