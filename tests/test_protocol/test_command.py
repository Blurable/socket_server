import pytest
import socket_chat.protocol as protocol

@pytest.fixture()
def command():
    command = protocol.chat_command()
    return command


@pytest.mark.parametrize('comm_type', [protocol.chat_command.COMM_TYPE.COMM_NULL.value, 
                                       protocol.chat_command.COMM_TYPE.COMM_MAX.value, 
                                       256])
def test_command_failure(command, comm_type):
    command.comm_type = comm_type
    with pytest.raises(protocol.ProtocolTypeException):
        assert command.pack()


def test_command_pack_unpack(command):
    command.comm_type = protocol.chat_command.COMM_TYPE.COMM_MEMBERS.value
    pkt = command.pack()

    test_command = protocol.chat_command()
    test_command.unpack(pkt[3:])
    assert test_command.comm_type == command.comm_type == protocol.chat_command.COMM_TYPE.COMM_MEMBERS.value


@pytest.mark.parametrize('comm_type', [(protocol.chat_command.COMM_TYPE.COMM_NULL.value),
                                       (protocol.chat_command.COMM_TYPE.COMM_MAX.value)])
def test_command_failure_unpack(command, comm_type):
    with pytest.raises(protocol.ProtocolTypeException):
        comm_type = comm_type.to_bytes(protocol.chat_command.COMMAND_TYPE_FIELD_SIZE, 'little')
        command.unpack(comm_type)