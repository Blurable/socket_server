import re
import socket
import threading

from socket_chat.tsdict import ThreadSafeDict
from socket_chat.connection import Connection
import socket_chat.protocol as protocol


def start_server(host_port, host_ip = socket.gethostbyname(socket.gethostname())):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((host_ip, host_port))
        server_socket.listen()
        print('[*]Server is listening...\n')
    except Exception as e:
        print(f'[-]Error while starting the server: {e}')
        server_socket.close()

    clients = ThreadSafeDict()
    while True:
        try:
            client_socket, client_addr = server_socket.accept()
            print(f"[*]Accepted connection from {client_addr[0]}:{client_addr[1]}")
            handler = ClientHandler(Connection(client_socket), clients)
            threading.Thread(target=handler.run, daemon=True).start()
        except Exception as e:
            print(f'[-]Error while accepting the client: {e}')
            client_socket.close()


class ClientHandler:
    def __init__(self, client: Connection, clients: ThreadSafeDict):
        self.client = client
        self.clients = clients
        self.username = ''
    
    
    def run(self):
        try:
            self.main_loop()
        except Exception as e:
            print(f'[-]Error: {e}')
        finally:
            self.shutdown()

    
    def main_loop(self):
        while True:
            hdr_bytes = self.client.recv(protocol.chat_header.PKT_TYPE_FIELD_SIZE + 
                                         protocol.chat_header.PKT_LEN_FIELD_SIZE)
            hdr = protocol.chat_header()
            hdr.unpack(hdr_bytes)

            payload = self.client.recv(hdr.msg_len)
            if len(payload) != hdr.msg_len:
                raise ValueError
            if not self.username and hdr.msg_type != protocol.MSG_TYPE.CHAT_CONNECT:
                break
            match hdr.msg_type:
                case protocol.MSG_TYPE.CHAT_CONNECT:
                    pkt = protocol.chat_connect()
                    pkt.unpack(payload)
                    self.handle_connect(pkt)
                case protocol.MSG_TYPE.CHAT_MSG:
                    pkt = protocol.chat_msg()
                    pkt.unpack(payload)
                    self.handle_msg(pkt)
                case protocol.MSG_TYPE.CHAT_DISCONNECT:
                    self.shutdown()
                    break
                case protocol.MSG_TYPE.CHAT_COMMAND:
                    pkt = protocol.chat_command()
                    pkt.unpack(payload)
                    self.handle_command(pkt)
                case _:
                    print(f"[-]Unexpected type {hdr.msg_type}")
                    self.shutdown()
                    break

    
    def handle_connect(self, pkt: protocol.chat_connect):
        reply = protocol.chat_connack()
        
        if pkt.protocol_version != protocol.SERVER_CONFIG.CURRENT_VERSION:
            reply.conn_type = protocol.chat_connack.CONN_TYPE.WRONG_PROTOCOL_VERSION
            self.client.send(reply.pack())
            return

        if pkt.username_validation(pkt.username):
            if self.clients.add_if_not_exists(pkt.username, self.client):
                print(f"[*]{pkt.username} has connected to the server")
                reply.conn_type = protocol.chat_connack.CONN_TYPE.CONN_ACCEPTED
                self.username = pkt.username
                self.client.send(reply.pack())
                return
        
        reply.conn_type = protocol.chat_connack.CONN_TYPE.CONN_RETRY
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
            case pkt.COMM_TYPE.COMM_MEMBERS:
                reply = protocol.chat_msg()
                reply.src = protocol.SERVER_CONFIG.SERVER_NAME
                reply.dst = self.username
                reply.msg = '\n'.join(self.clients.copy_keys())
                self.client.send(reply.pack())
            case _:
                print(f"[-]Unexpected type {pkt.comm_type}")
                self.shutdown()
                    

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