import socket
import asyncio

class ConnectionTimedOut():
    pass
class Connection:

    def __init__(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter):
        self.reader = client_reader
        self.writer = client_writer
        self.is_active = True
        self.sendLock = asyncio.Lock()


    # def get_addr(self):
    #     return self.writer.get_extra_info('peername')


    async def send(self, msg: bytes):
        self.writer.write(msg)
        await self.writer.drain()


    async def recv(self, len: int, timeout=None) -> bytes:
        try:
            msg = await asyncio.wait_for(self.reader.read(len), timeout)
            if not msg:
                raise socket.error
            return msg
        except TimeoutError:
            pass
    

    async def close(self):
        self.is_active = False
        self.writer.close()
        await self.writer.wait_closed()