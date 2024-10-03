import pytest
from unittest.mock import patch
import socket_chat.protocol as protocol


@pytest.mark.parametrize('start_client', [['Artyom', 'Baho']], indirect=True)
def test_client(start_client):
    client_list = []
    for _ in range(start_client.qsize()):
        client_list.append(start_client.get())

    for client in client_list:
        if client.username == 'Artyom':
            client.cur_channel = 'Baho'

            def mocked_sender(self):
                pkt = protocol.chat_command()
                pkt.comm_type = pkt.COMM_TYPE.COMM_MEMBERS
                self.server.send(pkt.pack())

            with patch.object(client, 'sender', side_effect=lambda: mocked_sender(client)):
                client.sender()

            hdr, payload = client.recv_pkt()
            assert hdr.msg_type == protocol.MSG_TYPE.CHAT_MSG
            pkt = protocol.chat_msg()
            pkt.unpack(payload)
            assert pkt.src == protocol.SERVER_CONFIG.SERVER_NAME
            assert pkt.dst == client.username
            assert pkt.msg == 'Artyom\nBaho' or pkt.msg == 'Baho\nArtyom'
