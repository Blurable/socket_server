from socket_chat.server import Server

if __name__ == '__main__':
    server = Server(54321)
    server.start_server()