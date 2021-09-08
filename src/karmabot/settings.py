import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv


def get_env_var(env_var: str, default: str = None) -> str:
    env_var_value = os.environ.get(env_var)

    # explicit check for None as None is returned by environ.get for non existing keys
    if env_var_value is None:
        if default is not None:
            return default

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
    logging.info("Loading environmental variables from: '%s'", dotenv_path)
    load_dotenv(dotenv_path)

# Environment variables
KARMABOT_ID = get_env_var("KARMABOT_SLACK_USER")
DATABASE_URL = get_env_var("KARMABOT_DATABASE_URL")
SLACK_APP_TOKEN = get_env_var("KARMABOT_SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = get_env_var("KARMABOT_SLACK_BOT_TOKEN")
TEST_MODE = bool(get_env_var("KARMABOT_TEST_MODE") == "true")
logging.info("Test mode enabled: %s", TEST_MODE)

# Slack
GENERAL_CHANNEL = get_env_var("KARMABOT_GENERAL_CHANNEL")
ADMINS = get_env_var("KARMABOT_ADMINS")
ADMINS = ADMINS.split(",")  # type: ignore

# Karma
# the first +/- is merely signaling, start counting (regex capture)
# from second +/- onwards, so bob++ adds 1 point, bob+++ = +2, etc
KARMA_ACTION_PATTERN = re.compile(
    r"(?:^| )(\S{2,}?)\s?[\+\-]([\+\-]+)", flags=re.MULTILINE
)
MAX_POINTS = 5
