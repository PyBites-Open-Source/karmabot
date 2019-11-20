import os
import re
from pathlib import Path

from dotenv import load_dotenv
from slackclient import SlackClient

dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path)

# Environment variables
KARMABOT_ID = os.environ.get("SLACK_KARMA_BOTUSER")
SLACK_TOKEN = os.environ.get("SLACK_KARMA_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")
SLACK_INVITE_TOKEN = os.environ.get("SLACK_KARMA_INVITE_USER_TOKEN")

# Slack
GENERAL_CHANNEL = "C4SFQJJ9Z"
ADMINS = ("U4RTDPKUH", "U4TN52NG6", "U4SJVFMEG", "UKS45DGFQ")  # bob, julian, pybites
SLACK_ID_FORMAT = re.compile(r"^<@[^>]+>$")
SLACK_CLIENT = SlackClient(SLACK_TOKEN)

# Karma
# the first +/- is merely signaling, start counting (regex capture)
# from second +/- onwards, so bob++ adds 1 point, bob+++ = +2, etc
KARMA_ACTION = re.compile(r"(?:^| )(\S{2,}?)\s?[\+\-]([\+\-]+)")
MAX_POINTS = 5
