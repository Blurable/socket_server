import pytest
import socket_chat.protocol as protocol
import threading
import asyncio
import time


def get_test_data():
    return [('/quit', ''), ('/members', ''), ('/info', ''), ('/all', ''), ('/', ''), ('/123321', ''), ('/ / /', ''), ('/asd ', ''),
            (' /asd', ''), ('', ''), (' ', ''), ('/1asd_', ''), ('/asd', 'asd'), ('/_123', '_123'), ('/_', '_'), ('/_1a', '_1a'), ('/A_a_A_a_A', 'A_a_A_a_A')]


@pytest.mark.parametrize('input, cur_channel', get_test_data())
@pytest.mark.asyncio
async def test_sender_channel_switch(mock_client, input, cur_channel):
    client, _, input_queue, _ = mock_client

    assert client.cur_channel == ''
    await input_queue.put(input)

    try:
        await asyncio.wait_for(client.sender(), 0.1)
    except:
        pass

    assert client.cur_channel == cur_channel

@pytest.mark.asyncio
async def test_sender_channel_all_switch(mock_client):
    client, _, input_queue, _ = mock_client

    client.cur_channel = 'Artyom'
    await input_queue.put('/all')
    try:
        await asyncio.wait_for(client.sender(), 0.1)
    except:
        pass

    assert client.cur_channel == ''
