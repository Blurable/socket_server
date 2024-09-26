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
    with pytest.raises(AssertionError):
        assert connect.pack()


def test_pack(connect):
    connect.hdr = protocol.chat_header(protocol.MSG_TYPE.CHAT_CONNECT)
    connect.username = 'Artyom'
    connect.protocol_version = protocol.SERVER_CONFIG.CURRENT_VERSION
    

    msg = protocol.MSG_TYPE.CHAT_CONNECT.to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE, 'little') + \
          (len(connect.username) + protocol.chat_connect.USERNAME_LEN_FIELD_SIZE + \
           len(connect.protocol_version) + protocol.chat_connect.PROTOCOL_VERSION_LEN_FIELD_SIZE).to_bytes(protocol.chat_header.PKT_LEN_FIELD_SIZE, 'little') + \
          len(connect.protocol_version).to_bytes(protocol.chat_connect.PROTOCOL_VERSION_LEN_FIELD_SIZE, 'little') + connect.protocol_version.encode() + \
          len(connect.username).to_bytes(protocol.chat_connect.USERNAME_LEN_FIELD_SIZE, 'little') + connect.username.encode()
    
    assert msg == connect.pack()


def test_unpack(connect):
    protocol_version = '1.2.3'
    username = 'Moytra'
    msg = len(protocol_version).to_bytes(protocol.chat_connect.PROTOCOL_VERSION_LEN_FIELD_SIZE, 'little') + protocol_version.encode() + \
          len(username).to_bytes(protocol.chat_connect.USERNAME_LEN_FIELD_SIZE, 'little') + username.encode()

    connect.unpack(msg)
    assert connect.username == username
    assert connect.protocol_version == protocol_version