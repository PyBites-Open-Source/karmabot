import logging
import os
import re
import sys

from slackclient import SlackClient
from bot.db import db_session


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",  # noqa E501
    datefmt="%m-%d %H:%M",
    filename="bot.log",
)

botuser_id = os.environ.get('SLACK_KARMA_BOTUSER')
token = os.environ.get('SLACK_KARMA_TOKEN')

if not botuser_id or not token:
    print("Make sure you set SLACK_KARMA_BOTUSER and SLACK_KARMA_TOKEN in env")
    sys.exit(1)

KARMABOT_ID = botuser_id
SLACK_CLIENT = SlackClient(token)


# Slack Real Time Messaging API - https://api.slack.com/rtm
if not SLACK_CLIENT.rtm_connect():
    logging.error("Connection Failed, invalid token?")
    sys.exit(1)

# Database
db_session.global_init()

# Regex
# the first +/- is merely signaling, start counting (regex capture)
# from second +/- onwards, so bob++ adds 1 point, bob+++ = +2, etc
KARMA_ACTION = re.compile(r"(?:^| )(\S{2,}?)\s?[\+\-]([\+\-]+)")
IS_USER = re.compile(r"^<@[^>]+>$")

# Constants
MAX_POINTS = 5

# Everything initialized
logging.info("Script started")
