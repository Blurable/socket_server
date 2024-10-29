import pytest
import socket_chat.protocol as protocol


@pytest.fixture
def disconnect():
    disconnect = protocol.chat_disconnect()
    return disconnect


def test_disconnect_pack(disconnect):
    msg = disconnect.pack()
    assert msg == protocol.MSG_TYPE.CHAT_DISCONNECT.value.to_bytes(protocol.chat_header.PKT_LEN_FIELD_SIZE, 'little') + \
                                                      (0).to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE, 'little')


def test_disconnect_unpack(disconnect):
    try:
        disconnect.unpack()
    except:
        assert False