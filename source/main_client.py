from socket_chat.client import Client
import logging.config
import json
import asyncio


async def main():
    client = Client(54321)
    await client.start_client()


if __name__ == '__main__':
    with open('client_logs\\logger_client_config.json', 'r') as f:
        config = json.load(f)
        logging.config.dictConfig(config)
        logger = logging.getLogger(__name__)
    logger.debug('main_server started')
    asyncio.run(main())