import socket
import threading


class Connection:
    def __init__(self, sock: socket.socket):
        self.sock = sock
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

        self.sendLock = threading.Lock()

        self.username = ''

    def send(self, msg: bytes):
        with self.sendLock:
            self.sock.sendall(msg)

    def recv(self, len: int) -> bytes:
        return self.sock.recv(len)
    
    def close(self):
        self.sock.close()