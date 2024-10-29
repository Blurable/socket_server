import pytest


def test_connection_error(test_client):
    client, _ = test_client
    assert client.server == None


def test_authorization_error(test_server, test_client):
    server, _, _ = test_server
    client, input_queue = test_client

    assert client.server != None

    username = 'Artyom'
    client.server.close()
    input_queue.put(username)
    
    assert client.server.is_active == False
    assert server.clients.get_if_exists(username) == None

    server.server_socket.close()


def test_connect_to_server_add_client(test_server, test_client):
    server, add_q, del_q = test_server
    client, input_q = test_client

    username = 'User'
    input_q.put(username)

    assert add_q.get() == username
    assert username in server.clients

    server.server_socket.close()


def test_disconnect_from_server_remove_client(test_client, test_server):
    server, add_q, del_q = test_server
    client, input_q = test_client

    username = 'User'
    input_q.put(username)

    assert add_q.get() == username
    assert username in server.clients

    client.server.close()

    assert del_q.get() == username
    assert username not in server.clients