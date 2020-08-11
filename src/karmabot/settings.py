import os
import re
from pathlib import Path

from dotenv import load_dotenv
from slackclient import SlackClient

dotenv_path = Path(".").resolve() / ".karmabot"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Environment variables
KARMABOT_ID = os.environ.get("KARMABOT_SLACK_USER")
SLACK_TOKEN = os.environ.get("KARMABOT_SLACK_TOKEN")
SLACK_INVITE_TOKEN = os.environ.get("KARMABOT_SLACK_INVITE_USER_TOKEN")
DATABASE_URL = os.environ.get("KARMABOT_DATABASE_URL")

# Slack
GENERAL_CHANNEL = os.environ.get("KARMABOT_GENERAL_CHANNEL")
ADMINS = os.environ.get("KARMABOT_ADMINS").split(",")  # type: ignore
SLACK_ID_FORMAT = re.compile(r"^<@[^>]+>$")
SLACK_CLIENT = SlackClient(SLACK_TOKEN)

# Karma
# the first +/- is merely signaling, start counting (regex capture)
# from second +/- onwards, so bob++ adds 1 point, bob+++ = +2, etc
KARMA_ACTION = re.compile(r"(?:^| )(\S{2,}?)\s?[\+\-]([\+\-]+)")
MAX_POINTS = 5
