from socket_chat.client import Client


if __name__ == '__main__':
    chat_server = Client(54321)
    chat_server.connect_to_server()