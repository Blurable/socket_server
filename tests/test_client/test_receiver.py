import pytest
import socket_chat.protocol as protocol
import asyncio

@pytest.mark.asyncio
async def test_client_receiver(mock_client):
    client, buffer_queue, _, _ = mock_client

    msg = protocol.chat_msg()
    msg.src = 'Art'
    msg.dst = 'Tra'
    msg.msg = 'Hello'
    await buffer_queue.put(msg.pack())
    await client.receiver()

@pytest.mark.asyncio
async def test_client_recv_not_full_pkt(mock_client):
    client, buffer_queue, _, _ = mock_client

    await buffer_queue.put(b'\x01\x00')
    await client.receiver()
    client.connection.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_recv_pkt(mock_client):
    client, buffer_q, _, _ = mock_client
    msg = protocol.chat_msg()
    msg.msg = 'Hello'
    msg.src = 'Asd'
    msg.dst = 'Dsa'
    packed_msg = msg.pack()
    await buffer_q.put(packed_msg)

    hdr, payload = await client.recv_pkt()

    test_hdr = protocol.chat_header()
    test_hdr.msg_type = protocol.MSG_TYPE.CHAT_MSG.value
    test_hdr.msg_len = len(msg.msg) + len(msg.src) + len(msg.dst) + \
                       protocol.chat_msg.DST_LEN_FIELD_SIZE + protocol.chat_msg.MSG_LEN_FIELD_SIZE + protocol.chat_msg.SRC_LEN_FIELD_SIZE

    assert hdr.msg_type == test_hdr.msg_type
    assert hdr.msg_len == test_hdr.msg_len
    assert payload == packed_msg[protocol.chat_header.PKT_LEN_FIELD_SIZE+protocol.chat_header.PKT_TYPE_FIELD_SIZE: ]
