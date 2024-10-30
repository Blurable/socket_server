from enum import Enum, auto


def bytes_limit(bytes_num):
    return 2**(8*bytes_num)-1


class WrongProtocolVersionError(Exception):
    def __init__(self, message='Incorrect Version Type'):
        self.message = message
        super().__init__(self.message)

class WrongProtocolTypeError(Exception):
    def __init__(self, message='Incorrect Type'):
        self.message = message
        super().__init__(self.message)

class SERVER_CONFIG:
    CURRENT_VERSION = '1.0.0'
    SERVER_NAME = 'sys'
    KEYWORDS = {
        'info' : 'all possible commands',
        'members' : 'all chat members',
        'username' : 'switch to PMs with this user',
        'all' : 'switch to allchat',
        'quit' : 'quit chat'
    }
    RESTRICTED_USERNAMES = list(KEYWORDS.keys()) + [SERVER_NAME]


class MSG_TYPE(Enum):
    CHAT_NULL = auto()
    CHAT_CONNECT = auto()
    CHAT_CONNACK = auto()
    CHAT_MSG = auto()
    CHAT_DISCONNECT = auto()
    CHAT_COMMAND = auto()
    CHAT_MAX = auto()


class chat_header:
    PKT_TYPE_FIELD_SIZE = 1
    PKT_LEN_FIELD_SIZE = 2

    def __init__(self, msg_type=MSG_TYPE.CHAT_NULL.value):
        self.msg_type = msg_type
        self.msg_len = 0

    def pack(self) -> bytes:
        if self.msg_len > bytes_limit(self.PKT_LEN_FIELD_SIZE):
            raise ValueError
        
        if not (MSG_TYPE.CHAT_NULL.value < self.msg_type < MSG_TYPE.CHAT_MAX.value):
            raise WrongProtocolTypeError

        return self.msg_type.to_bytes(self.PKT_TYPE_FIELD_SIZE, "little") + \
               self.msg_len.to_bytes(self.PKT_LEN_FIELD_SIZE, "little")

    def unpack(self, data: bytes):
        msg_type = data[:self.PKT_TYPE_FIELD_SIZE]
        self.msg_type = int.from_bytes(msg_type, "little")
        if not (MSG_TYPE.CHAT_NULL.value < self.msg_type < MSG_TYPE.CHAT_MAX.value):
            raise WrongProtocolTypeError
        msg_len  = data[ self.PKT_TYPE_FIELD_SIZE : self.PKT_TYPE_FIELD_SIZE+self.PKT_LEN_FIELD_SIZE]
        self.msg_len = int.from_bytes(msg_len, "little")


class chat_connect:
    PROTOCOL_VERSION_LEN_FIELD_SIZE = 1
    USERNAME_LEN_FIELD_SIZE = 1

    def __init__(self):
        self.hdr = chat_header(MSG_TYPE.CHAT_CONNECT.value)
        self.protocol_version = SERVER_CONFIG.CURRENT_VERSION
        self.username = ""


    def username_validation(self, username: str):
        if username.isidentifier() and username.lower() not in SERVER_CONFIG.RESTRICTED_USERNAMES:
            self.username = username
            return True
        return False
        

    def pack(self) -> bytes:
        if len(self.username) > bytes_limit(self.USERNAME_LEN_FIELD_SIZE) or \
           len(self.protocol_version) > bytes_limit(self.PROTOCOL_VERSION_LEN_FIELD_SIZE):
            raise ValueError
        
        self.hdr.msg_len = len(self.protocol_version) + self.PROTOCOL_VERSION_LEN_FIELD_SIZE + len(self.username) + self.USERNAME_LEN_FIELD_SIZE
        return self.hdr.pack() + len(self.protocol_version).to_bytes(self.PROTOCOL_VERSION_LEN_FIELD_SIZE, "little") + self.protocol_version.encode() + \
                                 len(self.username).to_bytes(self.USERNAME_LEN_FIELD_SIZE, "little") + self.username.encode()
    
    
    def unpack(self, payload: bytes):
        begin = 0

        protocol_len = int.from_bytes(payload[begin : self.PROTOCOL_VERSION_LEN_FIELD_SIZE], "little")
        begin += self.PROTOCOL_VERSION_LEN_FIELD_SIZE
        self.protocol_version = payload[begin : begin+protocol_len].decode()
        begin += protocol_len

        username_len = int.from_bytes(payload[begin : begin+self.USERNAME_LEN_FIELD_SIZE], "little")
        begin += self.USERNAME_LEN_FIELD_SIZE
        self.username = payload[begin : begin+username_len].decode()


class chat_connack:
    CONN_TYPE_FIELD_SIZE = 1
    class CONN_TYPE(Enum):
        CONN_NULL = auto()       
        WRONG_PROTOCOL_VERSION = auto()
        CONN_RETRY = auto()
        CONN_ACCEPTED = auto()
        CONN_MAX = auto()

    def __init__(self):
        self.hdr = chat_header(MSG_TYPE.CHAT_CONNACK.value)
        self.conn_type = self.CONN_TYPE.CONN_NULL.value

    def pack(self) -> bytes:
        if not (self.CONN_TYPE.CONN_NULL.value < self.conn_type < self.CONN_TYPE.CONN_MAX.value):
            raise WrongProtocolTypeError

        self.hdr.msg_len = self.CONN_TYPE_FIELD_SIZE
        return self.hdr.pack() + self.conn_type.to_bytes(self.CONN_TYPE_FIELD_SIZE, "little")
    
    def unpack(self, payload: bytes):
        self.conn_type = int.from_bytes(payload, "little")
        if not (self.CONN_TYPE.CONN_NULL.value < self.conn_type < self.CONN_TYPE.CONN_MAX.value):
            raise WrongProtocolTypeError

class chat_msg:
    SRC_LEN_FIELD_SIZE = 1
    DST_LEN_FIELD_SIZE = 1
    MSG_LEN_FIELD_SIZE = 2

    def __init__(self):
        self.hdr = chat_header(MSG_TYPE.CHAT_MSG.value)
        self.msg = ""
        self.src = ""
        self.dst = ""

    def pack(self) -> bytes:
        if  len(self.src) > bytes_limit(self.SRC_LEN_FIELD_SIZE) or \
            len(self.dst) > bytes_limit(self.DST_LEN_FIELD_SIZE) or \
            len(self.msg) > bytes_limit(self.MSG_LEN_FIELD_SIZE):
            raise ValueError
        
        self.hdr.msg_len = self.SRC_LEN_FIELD_SIZE + len(self.src) + \
                           self.DST_LEN_FIELD_SIZE + len(self.dst) + \
                           self.MSG_LEN_FIELD_SIZE + len(self.msg)
        return self.hdr.pack() + len(self.src).to_bytes(self.SRC_LEN_FIELD_SIZE, "little") + self.src.encode() + \
                                 len(self.dst).to_bytes(self.DST_LEN_FIELD_SIZE, "little") + self.dst.encode() + \
                                 len(self.msg).to_bytes(self.MSG_LEN_FIELD_SIZE, "little") + self.msg.encode()
    
    
    def unpack(self, payload: bytes):
        begin = 0

        src_len = int.from_bytes(payload[begin : self.SRC_LEN_FIELD_SIZE], "little")
        begin += self.SRC_LEN_FIELD_SIZE
        self.src = payload[begin : begin+src_len].decode()
        begin += src_len

        dest_len = int.from_bytes(payload[begin : begin+self.DST_LEN_FIELD_SIZE], "little")
        begin += self.DST_LEN_FIELD_SIZE
        self.dst = payload[begin : begin+dest_len].decode()
        begin += dest_len

        msg_len = int.from_bytes(payload[begin : begin+self.MSG_LEN_FIELD_SIZE], "little")
        begin += self.MSG_LEN_FIELD_SIZE
        self.msg = payload[begin : begin+msg_len].decode()
        begin += msg_len

    def __repr__(self):
        return "[" + (f"/pm/{self.src}" if self.dst else f"/all/{self.src}") + "]:" + self.msg


class chat_command:
    COMMAND_TYPE_FIELD_SIZE = 1

    class COMM_TYPE(Enum):
        COMM_NULL = auto()
        COMM_MEMBERS = auto()
        COMM_MAX = auto()

    def __init__(self):
        self.hdr = chat_header(MSG_TYPE.CHAT_COMMAND.value)
        self.comm_type = self.COMM_TYPE.COMM_NULL.value

    def pack(self) -> bytes:
        if not (self.COMM_TYPE.COMM_NULL.value < self.comm_type < self.COMM_TYPE.COMM_MAX.value):
            raise WrongProtocolTypeError

        self.hdr.msg_len = self.COMMAND_TYPE_FIELD_SIZE
        return self.hdr.pack() + self.comm_type.to_bytes(self.COMMAND_TYPE_FIELD_SIZE, "little")
    
    def unpack(self, payload: bytes):
        self.comm_type = int.from_bytes(payload, "little")
        if not (self.COMM_TYPE.COMM_NULL.value < self.comm_type < self.COMM_TYPE.COMM_MAX.value):
            raise WrongProtocolTypeError


class chat_disconnect:
    def __init__(self):
        self.hdr = chat_header(MSG_TYPE.CHAT_DISCONNECT.value)

    def pack(self) -> bytes:
        return self.hdr.pack()
    
    def unpack(self):
        pass