import logging
import sys
import time

from bot import KARMA_ACTION, SLACK_CLIENT
from bot.karma import process_karma_changes
from bot.slack import parse_next_msg

# Slack Real Time Messaging API - https://api.slack.com/rtm
if not SLACK_CLIENT.rtm_connect():
    logging.error("Connection Failed, invalid token?")
    sys.exit(1)


def main():
    while True:
        time.sleep(1)

        message = parse_next_msg()
        if not message:
            continue

        karma_changes = KARMA_ACTION.findall(message.text)
        if not karma_changes:
            continue

        logging.debug("karma changes: {}".format(str(karma_changes)))
        process_karma_changes(message, karma_changes)


if __name__ == "__main__":
    main()
