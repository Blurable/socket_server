import pytest
import socket_chat.protocol as protocol


@pytest.fixture()
def msg():
    msg = protocol.chat_msg()
    return msg



@pytest.mark.parametrize('src, dst, text', [
                        ('*'*256, '***', '***' ),
                        ('***', '*'*256, '***'),
                        ('***', '***', '*'*30000)
                        ])
def test_msg_failure(msg, src, dst, text):
    msg.src = src
    msg.dst = dst
    msg.msg = text*3
    with pytest.raises(AssertionError):
        assert msg.pack()


def test_msg_pack(msg):
    msg.src = 'Artyom'
    msg.dst = 'Moytra'
    msg.msg = 'Hello'
    text =  protocol.MSG_TYPE.CHAT_MSG.to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE) + \
            (len(msg.src) + len(msg.dst) + len(msg.msg) + protocol.chat_msg.SRC_LEN_FIELD_SIZE + \
            protocol.chat_msg.DST_LEN_FIELD_SIZE + protocol.chat_msg.MSG_LEN_FIELD_SIZE).to_bytes(protocol.chat_header.PKT_LEN_FIELD_SIZE, 'little') + \
            len(msg.src).to_bytes(protocol.chat_msg.SRC_LEN_FIELD_SIZE, "little") + msg.src.encode() + \
            len(msg.dst).to_bytes(protocol.chat_msg.DST_LEN_FIELD_SIZE, "little") + msg.dst.encode() + \
            len(msg.msg).to_bytes(protocol.chat_msg.MSG_LEN_FIELD_SIZE, "little") + msg.msg.encode()
    
    assert msg.pack() == text


def test_msg_unpack(msg):
    src = 'Moytra'
    dst = 'Artyom'
    text = 'HelloolleH'
    msg.unpack(len(src).to_bytes(protocol.chat_msg.SRC_LEN_FIELD_SIZE, "little") + src.encode() + \
               len(dst).to_bytes(protocol.chat_msg.DST_LEN_FIELD_SIZE, "little") + dst.encode() + \
               len(text).to_bytes(protocol.chat_msg.MSG_LEN_FIELD_SIZE, "little") + text.encode())
    
    assert msg.src == src
    assert msg.dst == dst
    assert msg.msg == text