import pytest
import socket_chat.protocol as protocol
import threading


def get_test_data():
    return [('/quit', ''), ('/members', ''), ('/info', ''), ('/all', ''), ('/', ''), ('/123321', ''), ('/ / /', ''), ('/asd ', ''),
            (' /asd', ''), ('', ''), (' ', ''), ('/1asd_', ''), ('/asd', 'asd'), ('/_123', '_123'), ('/_', '_'), ('/_1a', '_1a'), ('/A_a_A_a_A', 'A_a_A_a_A')]


@pytest.mark.parametrize('input, cur_channel', get_test_data())
def test_sender_channel_switch(mock_client, input, cur_channel):
    client, _, input_queue, _ = mock_client

    assert client.cur_channel == ''

    input_queue.put(input)
    threading.Thread(target=client.sender, daemon=True).start()
    client.stop_event.is_set()

    assert client.cur_channel == cur_channel


def test_sender_channel_all_switch(mock_client):
    client, _, input_queue, _ = mock_client

    client.cur_channel = 'Artyom'
    input_queue.put('/all')
    threading.Thread(target=client.sender, daemon = True).start()
    client.stop_event.is_set()

    assert client.cur_channel == ''
