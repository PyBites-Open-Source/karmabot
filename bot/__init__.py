from collections import Counter
import logging
import os
import pickle
import re

from slackclient import SlackClient

SLACK_CLIENT = SlackClient(os.environ.get('SLACK_KARMA'))

MAX_POINTS = 5
KARMA_BOT = 'U5Z6KGX4L'

KARMA_ACTION = re.compile(r'(?:^| )([^\+\- ]+)\s*([\+\-]+)')
IS_USER = re.compile(r'^<@[^>]+>$')

USERNAME_CACHE = {}
KARMA_CACHE = 'data'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',  # noqa E501
                    datefmt='%m-%d %H:%M',
                    filename='bot.log')

logging.info('Script started')

try:
    logging.info('Retrieving karma cache file')
    karmas = pickle.load(open(KARMA_CACHE, "rb"))
except FileNotFoundError:
    logging.info('No cache file starting new Counter object in memory')
    karmas = Counter()
