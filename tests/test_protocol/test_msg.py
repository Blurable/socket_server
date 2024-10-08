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
    with pytest.raises(ValueError):
        assert msg.pack()


def test_msg_pack_unpack(msg):
    msg.src = 'Artyom'
    msg.dst = 'Moytra'
    msg.msg = 'Hello'
    pkt = msg.pack()

    test_msg = protocol.chat_msg()
    test_msg.unpack(pkt[3:])

    assert test_msg.src == msg.src == 'Artyom'
    assert test_msg.dst == msg.dst == 'Moytra'
    assert test_msg.msg == msg.msg == 'Hello'