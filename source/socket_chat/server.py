import socket
import asyncio
import logging.config
from socket_chat.connection import Connection
import socket_chat.protocol as protocol

class Server:
    def __init__(self, host_port, host_ip = socket.gethostbyname(socket.gethostname())):
        self.logger = logging.getLogger(__name__)
        self.host_port = host_port
        self.host_ip = host_ip
        self.addr = (self.host_ip, self.host_port)
        self.clients: dict = {}
        self.server_socket: socket.socket = None


    async def start_server(self):
        try:
            self.server = await asyncio.start_server(self.client_handler, self.host_ip, self.host_port)
        except Exception as e:
            self.logger.exception(f'[-]Error while starting the server: {e}')
            self.server.close()
            raise
        self.logger.info('[*]Server is listening...\n')
        await self.server.serve_forever()

    
    async def client_handler(self, client_reader, client_writer):
        handler = ClientHandler(Connection(client_reader, client_writer), self.clients)
        await handler.run()


class ClientHandler:
    def __init__(self, client: Connection, clients: dict):
        self.logger = logging.getLogger(__name__)
        self.client = client
        self.clients = clients
        self.username = ''
        self.timeout = 5
    
    
    async def run(self):
        try:
            while self.client.is_active:
                hdr, payload = await self.recv_pkt()
                self.handle_pkt(hdr, payload)
        except Exception as e:
            self.logger.exception(f'[-]Error: {e}')
            self.shutdown()


    async def recv_pkt(self):
        hdr_len = protocol.chat_header.PKT_TYPE_FIELD_SIZE + protocol.chat_header.PKT_LEN_FIELD_SIZE
        hdr_bytes = b''
        hdr_bytes += await self.client.recv(hdr_len)
        
        while len(hdr_bytes) < hdr_len:
            hdr_bytes += await self.client.recv((hdr_len - len(hdr_bytes)), self.timeout)
        hdr = protocol.chat_header()
        hdr.unpack(hdr_bytes)

        payload_len = hdr.msg_len
        payload = b''
        while len(payload) < payload_len:
            payload += await self.client.recv((payload_len - len(payload)), self.timeout)
        return hdr, payload
    

    async def handle_pkt(self, hdr: protocol.chat_header, payload: bytes):
        if not self.username and hdr.msg_type != protocol.MSG_TYPE.CHAT_CONNECT.value:
            raise ValueError('Invalid packets from unauthorized user')
        match hdr.msg_type:
            case protocol.MSG_TYPE.CHAT_CONNECT.value:
                pkt = protocol.chat_connect()
                pkt.unpack(payload)
                await self.handle_connect(pkt)
            case protocol.MSG_TYPE.CHAT_MSG.value:
                pkt = protocol.chat_msg()
                pkt.unpack(payload)
                await self.handle_msg(pkt)
            case protocol.MSG_TYPE.CHAT_DISCONNECT.value:
                await self.shutdown()
            case protocol.MSG_TYPE.CHAT_COMMAND.value:
                pkt = protocol.chat_command()
                pkt.unpack(payload)
                await self.handle_command(pkt)
            case _:
                raise protocol.WrongProtocolTypeError(f"[-]Unexpected type {hdr.msg_type} in handle_pkt")

    
    async def handle_connect(self, pkt: protocol.chat_connect):
        reply = protocol.chat_connack()
        
        if pkt.protocol_version != protocol.SERVER_CONFIG.CURRENT_VERSION:
            reply.conn_type = protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value
            await self.client.send(reply.pack())
            raise protocol.WrongProtocolVersionError('[-]Wrong protocol version')

        if pkt.username not in self.clients:
            self.clients[pkt.username] = self.client
            self.logger.info(f"[*]{pkt.username} has connected to the server")
            reply.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value
            self.username = pkt.username
            await self.client.send(reply.pack())
            return

        reply.conn_type = protocol.chat_connack.CONN_TYPE.CONN_RETRY.value
        await self.client.send(reply.pack())


    async def handle_msg(self, pkt: protocol.chat_msg):
        self.logger.debug(pkt)

        if pkt.dst:
            if pkt.dst not in self.clients:
                fail_pkt = protocol.chat_msg()
                fail_pkt.src = protocol.SERVER_CONFIG.SERVER_NAME
                fail_pkt.dst = self.username
                fail_pkt.msg = f"{pkt.dst} is offline"
                await self.client.send(fail_pkt.pack())
            else:
                receiver = self.clients[pkt.dst]
                try:
                    await receiver.send(pkt.pack())
                except Exception as e:
                    self.logger.exception(f'Error {e} inside handle_msg')
                    pass
        else:
            await self.broadcast(pkt.pack())


    async def handle_command(self, pkt: protocol.chat_command):
        match pkt.comm_type:
            case pkt.COMM_TYPE.COMM_MEMBERS.value:
                reply = protocol.chat_msg()
                reply.src = protocol.SERVER_CONFIG.SERVER_NAME
                reply.dst = self.username
                clients = [k for k in self.clients.keys() if k != self.username]
                if not clients:
                    reply.msg = "You are alone in the chat"
                else:
                    reply.msg = '\n'.join(clients)
                await self.client.send(reply.pack())
            case _:
                raise protocol.WrongProtocolTypeError(f"[-]Unexpected type {pkt.comm_type}")
                    

    async def broadcast(self, msg: bytes):
        clients = [v for v in self.clients.values() if v != self.client]

        for client in clients:
            try:
                await client.send(msg)
            except Exception as e:
                self.logger.exception(f'[-]Error while broadcasting a message to {client}: {e}')


    async def shutdown(self):
        await self.client.close()
        if self.username:
            del self.clients[self.username] 

            pkt = protocol.chat_msg()
            pkt.src = protocol.SERVER_CONFIG.SERVER_NAME
            pkt.dst = ""
            pkt.msg = f"{self.username} disconnected"
            await self.broadcast(pkt.pack())