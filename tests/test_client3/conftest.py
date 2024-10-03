import pytest
import socket
from unittest.mock import patch
from socket_chat.client import Client
from socket_chat.connection import Connection
import socket_chat.server as server
from queue import Queue
import threading


def srvr():
    server.start_server(54321)

@pytest.fixture(scope='session', autouse=True)
def start_server():
    threading.Thread(target=srvr, daemon=True).start()


