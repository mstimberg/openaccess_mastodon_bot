import logging
import os

from .bot import Bot


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if 'MASTO_TOKEN' not in os.environ:
        raise RuntimeError('Need an access token (MASTO_TOKEN)')
    if 'EMAIL' not in os.environ:
        raise RuntimeError('Need an email address for API access (EMAIL)')
    bot = Bot()
    bot.start_stream()
