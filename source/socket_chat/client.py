import re
import socket
import asyncio
from aioconsole import ainput
import logging

from socket_chat.connection import Connection
import socket_chat.protocol as protocol


class Client:
    def __init__(self, server_port, server_ip = socket.gethostbyname(socket.gethostname())):
        self.logger = logging.getLogger(__name__)
        self.port = server_port
        self.host = server_ip
        self.sock: socket.socket = None
        self.connection: Connection = None
        self.username: str = ""
        self.cur_channel: str = ""


    async def connect_to_server(self):
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port)     
        except Exception as e:
            self.logger.exception(f'Error while connecting to server: {e}')
            return
        self.logger.info("[*]Successfull connection to the server")
        self.connection = Connection(reader, writer)

        
    async def recv_pkt(self):
        hdr_len = protocol.chat_header.PKT_TYPE_FIELD_SIZE + protocol.chat_header.PKT_LEN_FIELD_SIZE
        hdr_bytes = b''

        hdr_bytes += await self.connection.recv(hdr_len)
        while len(hdr_bytes) < hdr_len:
            hdr_bytes += await self.connection.recv(hdr_len - len(hdr_bytes))
        hdr = protocol.chat_header()
        hdr.unpack(hdr_bytes)

        payload_len = hdr.msg_len
        payload = b''
        while len(payload) < payload_len:
            payload += await self.connection.recv(payload_len - len(payload))
        
        return hdr, payload
        

    async def authorize(self):
        while self.connection.is_active:
            username = await ainput("[*]Please enter your username (must contain only letters):")
            conn = protocol.chat_connect()
            conn.username = username
            try:
                await self.connection.send(conn.pack())
            except protocol.InvalidUsernameError:
                self.logger.error(f"[*]Username {username} is not valid, try again")
                continue    

            hdr, payload = await self.recv_pkt()
            if hdr.msg_type != protocol.MSG_TYPE.CHAT_CONNACK.value:
                raise protocol.WrongProtocolTypeError("[-]Wrong msg type during authorize")
            pkt = protocol.chat_connack()
            pkt.unpack(payload)
            match pkt.conn_type:
                case protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value:
                    self.username = username
                    break
                case protocol.chat_connack.CONN_TYPE.CONN_RETRY.value:
                    self.logger.error(f"[*]Username {username} is already taken, try again")
                case protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value:
                    raise protocol.WrongProtocolVersionError("[-]Protocol version is out of date.")
                case _:
                    raise protocol.WrongProtocolTypeError("[-]Wrong connection type during authorize")


    def handle(self, hdr, payload):
        match hdr.msg_type:
            case protocol.MSG_TYPE.CHAT_MSG.value:
                pkt = protocol.chat_msg()
                pkt.unpack(payload)
                self.handle_msg(pkt)
            case _:
                raise protocol.WrongProtocolTypeError(f"[-]Unexpected type {hdr.msg_type} while handling the msg")


    def handle_msg(self, pkt: protocol.chat_msg):
        print("\n", pkt, sep='')


    def info(self):
        info = ''
        for key, value in protocol.SERVER_CONFIG.KEYWORDS.items():
            info += f'/{key}: {value}\n'
        return info


    async def sender(self):
        try:
            while self.connection.is_active:
                channel = self.cur_channel if self.cur_channel else "all"
                msg = await ainput(f"[/{channel}]:")
                match msg.lower():
                    case '/quit':
                        pkt = protocol.chat_disconnect()
                        await self.connection.send(pkt.pack())
                        self.logger.info('[*]Quitting chat')
                        await self.connection.close()
                    case '/info':
                        self.logger.debug(self.info())
                    case '/members':
                        pkt = protocol.chat_command()
                        pkt.comm_type = pkt.COMM_TYPE.COMM_MEMBERS.value
                        await self.connection.send(pkt.pack())
                    case '/all':
                        self.cur_channel = ""
                    case _ if re.fullmatch(r'^/[a-zA-Z_][a-zA-Z0-9_]*$', msg):
                        self.cur_channel = msg[1:]
                    case _:
                        pkt = protocol.chat_msg()
                        pkt.src = self.username
                        pkt.dst = self.cur_channel
                        pkt.msg = msg
                        await self.connection.send(pkt.pack())
        except Exception as e:
            print(f'Error in sender: {e}')
            await self.connection.close()
            

    async def receiver(self):
        try:
            while self.connection.is_active:
                hdr, payload = await self.recv_pkt()
                self.handle(hdr, payload)
        except Exception as e:
            self.logger.exception(f'[-]Error in receiver: {e}')
            await self.connection.close()


    async def start_client(self):
        await self.connect_to_server()
        
        try:
            await self.authorize()
        except Exception as e:
            self.logger.exception(f'Error while authorizing: {e}')
            self.connection.close()
            return
        self.logger.info("[*]Authorized!")
        self.logger.debug(self.info())

        receive_task = asyncio.create_task(self.receiver())
        send_task = asyncio.create_task(self.sender())
        done, pending = await asyncio.wait({receive_task, send_task}, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
