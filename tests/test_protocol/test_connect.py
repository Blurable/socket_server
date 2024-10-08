import pytest
import socket_chat.protocol as protocol

@pytest.fixture()
def connect():
    connect = protocol.chat_connect()
    return connect


@pytest.mark.parametrize('username, protocol_version_length', [
                        ('1'*256, '1'),
                        ('1', '1'*256)
                        ])
def test_pack_failure(connect, username, protocol_version_length):
    connect.username = username
    connect.protocol_version = protocol_version_length
    with pytest.raises(ValueError):
        assert connect.pack()


def test_connect_pack_unpack(connect):
    connect.username = 'Artyom'
    connect.protocol_version == protocol.SERVER_CONFIG.CURRENT_VERSION
    pkt = connect.pack()

    test_connect = protocol.chat_connect()
    test_connect.unpack(pkt[3:])
    
    assert test_connect.username == connect.username == 'Artyom'
    assert test_connect.protocol_version == connect.protocol_version == protocol.SERVER_CONFIG.CURRENT_VERSION
