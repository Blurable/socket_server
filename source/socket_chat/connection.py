import socket
import asyncio
import logging

class ConnectionTimedOutError(Exception):
    pass

class Connection:

    def __init__(self, client_reader: asyncio.StreamReader, client_writer: asyncio.StreamWriter):
        self.logger = logging.getLogger(__name__)
        self.reader = client_reader
        self.writer = client_writer
        self.is_active = True


    async def send(self, msg: bytes):
        self.writer.write(msg)
        await self.writer.drain()


    async def recv(self, len: int, timeout=None) -> bytes:
        try:
            msg = await asyncio.wait_for(self.reader.read(len), timeout)
            if not msg:
                raise ConnectionResetError
            return msg
        except TimeoutError:
            raise ConnectionTimedOutError
        except Exception:
            raise ConnectionResetError
    

    async def close(self):
        self.is_active = False
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except Exception as e:
            self.logger.error('Socket was already closed.')