import pytest
import socket_chat.protocol as protocol

@pytest.fixture()
def command():
    command = protocol.chat_command()
    return command


@pytest.mark.parametrize('comm_type', [protocol.chat_command.COMM_TYPE.COMM_NULL, 
                                       protocol.chat_command.COMM_TYPE.COMM_MAX, 
                                       256])
def test_command_failure(command, comm_type):
    command.comm_type = comm_type
    with pytest.raises(AssertionError):
        assert command.pack()


def test_command_pack(command):
    command.comm_type = protocol.chat_command.COMM_TYPE.COMM_MEMBERS
    connack_msg = protocol.MSG_TYPE.CHAT_COMMAND.to_bytes(protocol.chat_header.PKT_TYPE_FIELD_SIZE, 'little') + \
                  protocol.chat_command.COMMAND_TYPE_FIELD_SIZE.to_bytes(protocol.chat_header.PKT_LEN_FIELD_SIZE, 'little') + \
                  command.comm_type.to_bytes(protocol.chat_command.COMMAND_TYPE_FIELD_SIZE, 'little')
    assert connack_msg == command.pack()


def test_command_unpack(command):
    comm_type = protocol.chat_command.COMM_TYPE.COMM_MEMBERS
    command.unpack(comm_type.to_bytes(protocol.chat_command.COMMAND_TYPE_FIELD_SIZE, 'little'))
    assert command.comm_type == comm_type