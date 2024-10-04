import pytest
import socket_chat.protocol as protocol
import threading


def get_test_data():
    return [('/quit', ''), ('/members', ''), ('/info', ''), ('/all', ''), ('/', ''), ('/123321', ''), ('/ / /', ''), ('/asd ', ''),
            (' /asd', ''), ('', ''), (' ', ''), ('/1asd_', ''), ('/asd', 'asd'), ('/_123', '_123'), ('/_', '_'), ('/_1a', '_1a'), ('/A_a_A_a_A', 'A_a_A_a_A')]


@pytest.mark.parametrize('send, cur_channel', get_test_data())
def test_sender_channel_no_switch(mock_client, send, cur_channel):
    client, _, input_queue = mock_client
    assert client.cur_channel == ''
    input_queue.put(send)
    threading.Thread(target=client.sender, daemon=True).start()
    client.stop_event.is_set()
    assert client.cur_channel == cur_channel