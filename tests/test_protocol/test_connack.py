import pytest
import socket_chat.protocol as protocol


@pytest.fixture()
def connack():
    connack = protocol.chat_connack()
    return connack


@pytest.mark.parametrize('conn_type', [protocol.chat_connack.CONN_TYPE.CONN_NULL.value, 
                                       protocol.chat_connack.CONN_TYPE.CONN_MAX.value, 
                                       256])
def test_connack_failure(connack, conn_type):
    connack.conn_type = conn_type
    with pytest.raises(ValueError):
        assert connack.pack()


@pytest.mark.parametrize('conn_type', [(protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value),
                                       (protocol.chat_connack.CONN_TYPE.CONN_RETRY.value),
                                       (protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value)])
def test_connack_pack_unpack(connack, conn_type):
    connack.conn_type = conn_type
    pkt = connack.pack()

    test_connack = protocol.chat_connack()
    test_connack.unpack(pkt[3:])
    
    assert test_connack.conn_type == connack.conn_type == conn_type



