import re
import socket
import threading

from socket_chat.connection import Connection
import socket_chat.protocol as protocol


class Client:
    def __init__(self, server_port, server_ip = socket.gethostbyname(socket.gethostname())):
        self.serv_addr = (server_ip, server_port)

        self.sock: socket.socket = None
        self.server: Connection = None
        self.username: str = ""
        self.cur_channel: str = ""


    def connect_to_server(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(self.serv_addr)      
        except Exception as e:
            print(f'Error while connecting to server: {e}')
            self.sock.close()
            return
        self.server = Connection(self.sock)

        try:
            self.authorize()
        except Exception as e:
            print(f'Error while authorizing: {e}')
            self.server.close()
            return
        print("[*]Authorized!")
        print(self.info())

        threading.Thread(target=self.receiver, daemon=True).start()
        self.sender()

        
    def recv_pkt(self):
        hdr_len = protocol.chat_header.PKT_TYPE_FIELD_SIZE + protocol.chat_header.PKT_LEN_FIELD_SIZE
        hdr_bytes = b''

        hdr_bytes += self.server.recv(hdr_len)
        while len(hdr_bytes) < hdr_len:
            hdr_bytes += self.server.recv(hdr_len - len(hdr_bytes))
        hdr = protocol.chat_header()
        hdr.unpack(hdr_bytes)

        payload_len = hdr.msg_len
        payload = b''
        while len(payload) < payload_len:
            payload += self.server.recv(payload_len - len(payload))
        
        return hdr, payload
        

    def wrap_input(self, input_msg: str):
        msg = input(input_msg)
        return msg


    def authorize(self):
        while self.server.is_active:
            username = self.wrap_input("[*]Please enter your username (must contain only letters):")
            conn = protocol.chat_connect()
            if conn.username_validation(username):
                self.server.send(conn.pack())

                hdr, payload = self.recv_pkt()
                if hdr.msg_type == protocol.MSG_TYPE.CHAT_CONNACK.value:
                    pkt = protocol.chat_connack()
                    pkt.unpack(payload)
                    match pkt.conn_type:
                        case protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value:
                            self.username = username
                            break
                        case protocol.chat_connack.CONN_TYPE.CONN_RETRY.value:
                            print("[*]Username is already taken, try again")
                        case protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value:
                            raise protocol.WrongProtocolVersionError("[*]Protocol version is out of date.")
                        case _:
                            raise protocol.WrongProtocolTypeError("[-]Wrong connection type during authorize")
                else:
                    raise protocol.WrongProtocolTypeError("[-]Wrong msg type during authorize")
            else:
                print("[*]Username is not valid, try again")    


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


    def sender(self):
        try:
            while self.server.is_active:
                channel = self.cur_channel if self.cur_channel else "all"
                msg = self.wrap_input(f"[/{channel}]:")
                match msg.lower():
                    case '/quit':
                        pkt = protocol.chat_disconnect()
                        self.server.send(pkt.pack())
                        print('[*]Quitting chat')
                        self.server.close()
                    case '/info':
                        print(self.info())
                    case '/members':
                        pkt = protocol.chat_command()
                        pkt.comm_type = pkt.COMM_TYPE.COMM_MEMBERS.value
                        self.server.send(pkt.pack())
                    case '/all':
                        self.cur_channel = ""
                    case _ if re.fullmatch(r'^/[a-zA-Z_][a-zA-Z0-9_]*$', msg):
                        self.cur_channel = msg[1:]
                    case _:
                        pkt = protocol.chat_msg()
                        pkt.src = self.username
                        pkt.dst = self.cur_channel
                        pkt.msg = msg
                        self.server.send(pkt.pack())
        except Exception as e:
            print(f'Error in sender: {e}')
            self.server.close()
            

    def receiver(self):
        try:
            while self.server.is_active:
                hdr, payload = self.recv_pkt()
                self.handle(hdr, payload)
        except Exception as e:
            print(f'[-]Error in receiver: {e}')
            self.server.close()