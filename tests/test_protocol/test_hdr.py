import pytest
import socket_chat.protocol as protocol
import random


@pytest.fixture()
def hdr():
    hdr = protocol.chat_header()
    return hdr


def test_valueerror_pack(hdr):
    with pytest.raises(ValueError):
        hdr.msg_len = 65536
        hdr.msg_type = 1
        hdr.pack()


@pytest.mark.parametrize('hdr_len, msg_type', [(1, protocol.MSG_TYPE.CHAT_NULL.value), (1, protocol.MSG_TYPE.CHAT_MAX.value)])
def test_type_exception_pack(hdr, hdr_len, msg_type):
    with pytest.raises(protocol.WrongProtocolTypeError):
        hdr.msg_len = hdr_len
        hdr.msg_type = msg_type
        hdr.pack()


def get_test_msg_types():
    return [(msg_type.value) for msg_type in list(protocol.MSG_TYPE)][1:-1]

@pytest.mark.parametrize('msg_type', get_test_msg_types())
def test_hdr_pack_unpack(hdr, msg_type):
    hdr.msg_type = msg_type
    hdr.msg_len = 1
    pkt = hdr.pack()

    test_hdr = protocol.chat_header()
    test_hdr.unpack(pkt)
    
    assert test_hdr.msg_type == hdr.msg_type == msg_type
    assert test_hdr.msg_len == hdr.msg_len == 1


@pytest.mark.parametrize('msg_type', [(protocol.MSG_TYPE.CHAT_NULL.value),
                                       (protocol.MSG_TYPE.CHAT_MAX.value)])
def test_hdr_failure_unpack(hdr, msg_type):
    with pytest.raises(protocol.WrongProtocolTypeError):
        msg_type = msg_type.to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE, 'little')
        hdr.unpack(msg_type)
