import pytest
import socket
import time


def test_connection_error(test_client):
    client, _ = test_client
    assert client.server == None


def test_authorization_error(test_server, test_client):
    server, _, _ = test_server
    client, input_queue = test_client

    assert client.server != None

    client.server.close()
    input_queue.put('Artyom')
    
    assert client.server.is_active == False
    assert len(server.clients) == 0


def test_connect_to_server(test_server, test_client):
    server, add_q, del_q = test_server
    client, input_q = test_client

    username = 'User'
    input_q.put(username)
    client.server.is_active = False
    assert add_q.get() == username
    assert username in server.clients