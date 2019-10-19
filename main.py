import logging
import time

from bot import KARMA_ACTION
from bot.karma import process_karma_changes
from bot.slack import parse_next_msg


def main():
    while True:
        time.sleep(1)

        # Processes all interaction but karma changes
        message = parse_next_msg()
        if not message:
            continue

        # Finds and processes karma changes
        karma_changes = KARMA_ACTION.findall(message.text)
        if not karma_changes:
            continue

        logging.debug(f"Karma changes: {str(karma_changes)}")
        process_karma_changes(message, karma_changes)


if __name__ == "__main__":
    main()
