from socket_chat.server import Server
import logging.config
import json
import asyncio


async def main():
    server = Server(54321)
    await server.start_server()


if __name__ == '__main__':
    with open('logger_config.json', 'r') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
        logger = logging.getLogger(__name__)
    logger.debug('main_server started')
    asyncio.run(main())
