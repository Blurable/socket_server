import pytest
import socket_chat.protocol as protocol

@pytest.mark.asyncio
async def test_authorization_retry(mock_client):
    client, recv_queue, input_queue, send_queue = mock_client

    await input_queue.put('Baho')
    pkt1 = protocol.chat_connack()
    pkt1.conn_type = protocol.chat_connack.CONN_TYPE.CONN_RETRY.value
    await recv_queue.put(pkt1.pack())

    await input_queue.put('Artyom')
    pkt2 = protocol.chat_connack()
    pkt2.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value
    await recv_queue.put(pkt2.pack())
    
    await client.authorize()

    connect = protocol.chat_connect()
    connect.username = 'Baho'
    assert await send_queue.get() == connect.pack()
    connect.username = 'Artyom'
    assert await send_queue.get() == connect.pack()

    assert client.username == 'Artyom'

@pytest.mark.parametrize('keyword', [(k) for k in protocol.SERVER_CONFIG.KEYWORDS.keys()])
@pytest.mark.asyncio
async def test_authorization_invalid_nickname(mock_client, keyword):
    client, recv_queue, input_queue, send_queue = mock_client

    await input_queue.put(keyword)

    await input_queue.put('Artyom')
    pkt1 = protocol.chat_connack()
    pkt1.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value
    await recv_queue.put(pkt1.pack())
    
    await client.authorize()

    connect = protocol.chat_connect()
    connect.username = 'Artyom'
    assert await send_queue.get() == connect.pack()

    assert client.username == 'Artyom'
