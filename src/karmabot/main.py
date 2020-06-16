import logging
import time

from karmabot.db import db_session
from karmabot.karma import process_karma_changes
from karmabot.settings import KARMA_ACTION
from karmabot.slack import check_connection, parse_next_msg


def main():

    db_session.global_init()
    check_connection()

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

        logging.info(f"Karma changes: {str(karma_changes)}")
        process_karma_changes(message, karma_changes)


if __name__ == "__main__":
    main()
