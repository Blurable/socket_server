import threading
import socket


class Connection:

    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.is_active = True

        self.sendLock = threading.Lock()


    def send(self, msg: bytes):
        with self.sendLock:
            self.sock.sendall(msg)


    def recv(self, len: int) -> bytes:
        msg = self.sock.recv(len)
        if not msg:
            raise socket.error
        return msg
    

    def close(self):
        self.is_active = False
        self.sock.close()


    def settimeout(self, time):
        self.sock.settimeout(time)