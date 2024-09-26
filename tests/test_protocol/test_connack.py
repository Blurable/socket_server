import pytest
import socket_chat.protocol as protocol


@pytest.fixture()
def connack():
    connack = protocol.chat_connack()
    return connack


@pytest.mark.parametrize('conn_type', [protocol.chat_connack.CONN_TYPE.CONN_NULL, 
                                       protocol.chat_connack.CONN_TYPE.CONN_MAX, 
                                       256])
def test_connack_failure(connack, conn_type):
    connack.conn_type = conn_type
    with pytest.raises(AssertionError):
        assert connack.pack()


def test_connack_pack(connack):
    connack.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED
    connack_msg = protocol.MSG_TYPE.CHAT_CONNACK.to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE, 'little') + \
                  protocol.chat_connack.CONN_TYPE_FIELD_SIZE.to_bytes(protocol.chat_header.PKT_LEN_FIELD_SIZE, 'little') + \
                  connack.conn_type.to_bytes(protocol.chat_connack.CONN_TYPE_FIELD_SIZE, 'little')
    assert connack_msg == connack.pack()


def test_connack_unpack(connack):
    conn_type = protocol.chat_connack.CONN_TYPE.CONN_RETRY
    connack.unpack(conn_type.to_bytes(protocol.chat_connack.CONN_TYPE_FIELD_SIZE, 'little'))
    assert connack.conn_type == conn_type

