import pytest
import socket_chat.protocol as protocol


@pytest.mark.parametrize("username, flag_status", [
    ('', False),
    ('sys', False),
    ('username', False),
    ('members', False),
    ('all', False),
    ('info', False),
    ('quit', False),
    ('Artyom', True),
    (' ', False),
    ('123asd', False),
    ('asd123', True),
    ('@!#@!$', False),
    ('asd!', False),
    ('!asd', False),
    ('ArTyOm1234567890', True),
    ('a', True),
    ('123_asd', False),
    ('_123asd', True),
    ('asd_123', True)

])
def test_client_usernames(username, flag_status):
    obj = protocol.chat_connect()
    assert obj._chat_connect__username_validation(username) == flag_status


    



        
