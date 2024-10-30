import socket
import threading
import errno

from socket_chat.tsdict import ThreadSafeDict
from socket_chat.connection import Connection
import socket_chat.protocol as protocol

class Server:
    def __init__(self, host_port, host_ip = socket.gethostbyname(socket.gethostname())):
        self.host_port = host_port
        self.host_ip = host_ip
        self.addr = (self.host_ip, self.host_port)
        self.clients = ThreadSafeDict()
        self.server_socket: socket.socket = None


    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.bind(self.addr)
            self.server_socket.listen()
        except Exception as e:
            print(f'[-]Error while starting the server: {e}')
            self.server_socket.close()
            raise
        print('[*]Server is listening...\n')
        self.accept_clients()


    def accept_clients(self):
        while True:
            try:
                client_socket, client_addr = self.server_socket.accept()
                print(f"[*]Accepted connection from {client_addr[0]}:{client_addr[1]}")
                handler = ClientHandler(Connection(client_socket), self.clients)
                threading.Thread(target=handler.run, daemon=True).start()
            except socket.error as e:
                if e.errno == errno.WSAENOTSOCK:
                    print(f'[-]Server socket was closed while accepting clients')
                    raise
                else:
                    print(f'[-]Socket error while accepting clients: {e}')
            except Exception as e:
                print(f'[-]Exception error while accepting clients: {e}')
                if client_socket:
                    client_socket.close()
                


class ClientHandler:
    def __init__(self, client: Connection, clients: ThreadSafeDict):
        self.client = client
        self.clients = clients
        self.username = ''
    
    
    def run(self):
        try:
            while self.client.is_active:
                hdr, payload = self.recv_pkt()
                self.handle_pkt(hdr, payload)
        except Exception as e:
            print(f'[-]Error: {e}')
            self.shutdown()


    def recv_pkt(self):
        hdr_len = protocol.chat_header.PKT_TYPE_FIELD_SIZE + protocol.chat_header.PKT_LEN_FIELD_SIZE
        hdr_bytes = b''
        hdr_bytes += self.client.recv(hdr_len)
        
        self.client.settimeout(5)
        while len(hdr_bytes) < hdr_len:
            hdr_bytes += self.client.recv(hdr_len - len(hdr_bytes))
        hdr = protocol.chat_header()
        hdr.unpack(hdr_bytes)

        payload_len = hdr.msg_len
        payload = b''
        while len(payload) < payload_len:
            payload += self.client.recv(payload_len - len(payload))
        self.client.settimeout(None)
        return hdr, payload
    

    def handle_pkt(self, hdr, payload):
        if not self.username and hdr.msg_type != protocol.MSG_TYPE.CHAT_CONNECT.value:
            raise ValueError('Invalid packets from unauthorized user')
        match hdr.msg_type:
            case protocol.MSG_TYPE.CHAT_CONNECT.value:
                pkt = protocol.chat_connect()
                pkt.unpack(payload)
                self.handle_connect(pkt)
            case protocol.MSG_TYPE.CHAT_MSG.value:
                pkt = protocol.chat_msg()
                pkt.unpack(payload)
                self.handle_msg(pkt)
            case protocol.MSG_TYPE.CHAT_DISCONNECT.value:
                self.shutdown()
            case protocol.MSG_TYPE.CHAT_COMMAND.value:
                pkt = protocol.chat_command()
                pkt.unpack(payload)
                self.handle_command(pkt)
            case _:
                raise protocol.WrongProtocolTypeError(f"[-]Unexpected type {hdr.msg_type}")

    
    def handle_connect(self, pkt: protocol.chat_connect):
        reply = protocol.chat_connack()
        
        if pkt.protocol_version != protocol.SERVER_CONFIG.CURRENT_VERSION:
            reply.conn_type = protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION.value
            self.client.send(reply.pack())
            raise protocol.WrongProtocolVersionError('[-]Wrong protocol version')

        if self.clients.add_if_not_exists(pkt.username, self.client):
            print(f"[*]{pkt.username} has connected to the server")
            reply.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED.value
            self.username = pkt.username
            self.client.send(reply.pack())
            return

        reply.conn_type = protocol.chat_connack.CONN_TYPE.CONN_RETRY.value
        self.client.send(reply.pack())


    def handle_msg(self, pkt: protocol.chat_msg):
        print(pkt)

        fail = False
        if pkt.dst:
            receiver = self.clients.get_if_exists(pkt.dst)
            if receiver:
                try:
                    receiver.send(pkt.pack())
                except:
                    fail = True
            else:
                fail = True

            if fail:
                fail_pkt = protocol.chat_msg()
                fail_pkt.src = protocol.SERVER_CONFIG.SERVER_NAME
                fail_pkt.dst = self.username
                fail_pkt.msg = f"{pkt.dst} is offline"
                self.client.send(fail_pkt.pack())
        else:
            self.broadcast(pkt.pack())


    def handle_command(self, pkt: protocol.chat_command):
        match pkt.comm_type:
            case pkt.COMM_TYPE.COMM_MEMBERS.value:
                reply = protocol.chat_msg()
                reply.src = protocol.SERVER_CONFIG.SERVER_NAME
                reply.dst = self.username
                clients = self.clients.copy_keys()
                clients.remove(self.username)
                if not clients:
                    reply.msg = "You are alone in the chat"
                else:
                    reply.msg = '\n'.join(self.clients.copy_keys())
                self.client.send(reply.pack())
            case _:
                raise protocol.WrongProtocolTypeError(f"[-]Unexpected type {pkt.comm_type}")
                    

    def broadcast(self, msg: bytes):
        clients = self.clients.copy_values()
        if self.client in clients:
            clients.remove(self.client)

        for client in clients:
            try:
                client.send(msg)
            except Exception as e:
                print(f'[-]Error while broadcasting a message to {client}: {e}')


    def shutdown(self):
        self.client.close()
        if self.username:
            del self.clients[self.username] 

            pkt = protocol.chat_msg()
            pkt.src = protocol.SERVER_CONFIG.SERVER_NAME
            pkt.dst = ""
            pkt.msg = f"{self.username} disconnected"
            self.broadcast(pkt.pack())