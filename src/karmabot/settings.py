import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from slackclient import SlackClient


def _get_env_var(env_var: str):
    env_var_value = os.environ.get(env_var)

    # explicit check for None as None is returned by environ.get for non existing keys
    if env_var_value is None:
        raise KeyError(
            f"{env_var} was not found. Please check your .karmabot file as well as the README.md."
        )

    if not env_var_value:
        raise ValueError(
            f"{env_var} was found but seems empty. Please check your .karmabot file as well as the README.md."
        )

    return env_var_value


dotenv_path = Path(".").resolve() / ".karmabot"
if dotenv_path.exists():
    logging.info("Loading environmental variables from .karmabot.")
    load_dotenv(dotenv_path)

# Environment variables
KARMABOT_ID = _get_env_var("KARMABOT_SLACK_USER")
SLACK_TOKEN = _get_env_var("KARMABOT_SLACK_TOKEN")
SLACK_INVITE_TOKEN = _get_env_var("KARMABOT_SLACK_INVITE_USER_TOKEN")
DATABASE_URL = _get_env_var("KARMABOT_DATABASE_URL")

# Slack
GENERAL_CHANNEL = _get_env_var("KARMABOT_GENERAL_CHANNEL")
ADMINS = _get_env_var("KARMABOT_ADMINS")
ADMINS = ADMINS.split(",")  # type: ignore
SLACK_ID_FORMAT = re.compile(r"^<@[^>]+>$")
SLACK_CLIENT = SlackClient(SLACK_TOKEN)

# Karma
# the first +/- is merely signaling, start counting (regex capture)
# from second +/- onwards, so bob++ adds 1 point, bob+++ = +2, etc
KARMA_ACTION = re.compile(r"(?:^| )(\S{2,}?)\s?[\+\-]([\+\-]+)", flags=re.MULTILINE)
MAX_POINTS = 5
