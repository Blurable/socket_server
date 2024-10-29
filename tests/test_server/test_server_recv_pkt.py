import pytest
import socket
import socket_chat.protocol as protocol

@pytest.mark.parametrize('pkt, payload', [(b'\x03\x01\x00\x03', b'\x03'), (b'\x06\x00\x00', b'')])
def test_recv_pkt(mock_client_handler, pkt, payload):
    client, buffer_queue, _ = mock_client_handler
    buffer_queue.put(pkt)
    hdr, payload = client.recv_pkt()
    assert isinstance(hdr, protocol.chat_header)
    assert payload == payload