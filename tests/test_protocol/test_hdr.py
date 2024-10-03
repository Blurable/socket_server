import pytest
import socket_chat.protocol as protocol

@pytest.fixture()
def hdr():
    hdr = protocol.chat_header()
    return hdr



def test_failure_pack(hdr):
    with pytest.raises(AssertionError):
        hdr.pack()

    with pytest.raises(AssertionError):
        hdr.msg_len = 65536
        hdr.pack()


def test_pack(hdr):
    hdr.msg_type = 1
    expected_pack = hdr.msg_type.to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE, 'little') + \
                    hdr.msg_len.to_bytes(protocol.chat_header.PKT_LEN_FIELD_SIZE, 'little')
    assert expected_pack == hdr.pack()


def test_unpack(hdr):
    msg_len = 65533
    msg_type = 2
    hdr.unpack(msg_type.to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE, 'little') + \
               msg_len.to_bytes(protocol.chat_header.PKT_LEN_FIELD_SIZE, 'little'))
    assert hdr.msg_len == msg_len
    assert hdr.msg_type == msg_type