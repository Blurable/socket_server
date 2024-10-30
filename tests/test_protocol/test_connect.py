import pytest
import socket_chat.protocol as protocol

@pytest.fixture()
def connect():
    connect = protocol.chat_connect()
    return connect


@pytest.mark.parametrize('username, protocol_version_length, error', [
                        ('1'*256, '1', protocol.InvalidUsernameError),
                        ('Normal_username', '1'*256, protocol.WrongProtocolVersionError)
                        ])
def test_pack_length_errors(connect, username, protocol_version_length, error):
    connect.username = username
    connect.protocol_version = protocol_version_length
    with pytest.raises(error):
        assert connect.pack()


def test_connect_pack_unpack(connect):
    connect.username = 'Artyom'
    connect.protocol_version == protocol.SERVER_CONFIG.CURRENT_VERSION
    pkt = connect.pack()

    test_connect = protocol.chat_connect()
    test_connect.unpack(pkt[3:])
    
    assert test_connect.username == connect.username == 'Artyom'
    assert test_connect.protocol_version == connect.protocol_version == protocol.SERVER_CONFIG.CURRENT_VERSION


@pytest.mark.parametrize('username', [(username) for username in protocol.SERVER_CONFIG.KEYWORDS])
def test_connect_pack_errors(connect, username):
    connect.username = username
    
    with pytest.raises(protocol.InvalidUsernameError):
        connect.pack()

@pytest.mark.parametrize('username', [(username) for username in protocol.SERVER_CONFIG.KEYWORDS])
def test_connect_unpack_errors(connect, username):
    connect.username = username
    payload = len(connect.protocol_version).to_bytes(connect.PROTOCOL_VERSION_LEN_FIELD_SIZE, "little") + connect.protocol_version.encode() + \
              len(connect.username).to_bytes(connect.USERNAME_LEN_FIELD_SIZE, "little") + connect.username.encode()
    
    with pytest.raises(protocol.InvalidUsernameError):
        connect.unpack(payload)

