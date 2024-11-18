import pytest
import asyncio
from unittest.mock import patch
import socket_chat.protocol as protocol

buffer_queue = asyncio.Queue()
buffer = b''

async def recv_side_effect(bufsize, timeout=None):
    global buffer_queue, buffer

    if bufsize and not buffer:
        buffer += await asyncio.wait_for(buffer_queue.get(), timeout)
        
    chunk = buffer[ : bufsize]
    buffer = buffer[bufsize : ]
    return chunk  


def recv_data():
    hdr_len = protocol.chat_header.PKT_LEN_FIELD_SIZE + protocol.chat_header.PKT_TYPE_FIELD_SIZE

    command = protocol.chat_command()
    command.comm_type = command.COMM_TYPE.COMM_MEMBERS.value

    connect = protocol.chat_connect()
    connect.username = 'test_username'

    msg = protocol.chat_msg()

    return [(command.pack(), command.hdr, command.pack()[hdr_len:]), (connect.pack(), connect.hdr, connect.pack()[hdr_len:]),
            (msg.pack(), msg.hdr, msg.pack()[hdr_len:])]


@pytest.mark.parametrize('pkt, hdr, payload', recv_data())
@pytest.mark.asyncio
async def test_recv_pkt(client_handler_fixture, pkt, hdr, payload):
    await buffer_queue.put(pkt)
    client_handler_fixture.client.recv.side_effect = recv_side_effect

    h, p = await client_handler_fixture.recv_pkt()

    assert h.msg_type == hdr.msg_type
    assert h.msg_len == hdr.msg_len
    assert p == payload


@pytest.mark.asyncio
async def test_recv_pkt_timeout_error(client_handler_fixture):
    await buffer_queue.put(b'\x00\x00')
    client_handler_fixture.client.recv.side_effect = recv_side_effect

    with pytest.raises(TimeoutError):
        await asyncio.wait_for(client_handler_fixture.recv_pkt(), 5)


    
