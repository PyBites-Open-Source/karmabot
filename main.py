import logging
import pickle
import sys
import time

from bot import SLACK_CLIENT, KARMA_CACHE, KARMA_ACTION, karmas
from bot.slack import post_msg, parse_next_msg, lookup_username
from bot.karma import Karma, parse_karma_change

SAVE_INTERVAL = 60

# Slack Real Time Messaging API - https://api.slack.com/rtm
if not SLACK_CLIENT.rtm_connect():
    logging.error('Connection Failed, invalid token?')
    sys.exit(1)


def _save_cache():
    pickle.dump(karmas, open(KARMA_CACHE, "wb"))


def _process_karma_changes(message, karma_changes):
    for karma_change in karma_changes:
        giver = lookup_username(message.giverid)
        channel = message.channel

        receiver, points = parse_karma_change(karma_change)

        karma = Karma(giver, receiver)

        try:
            msg = karma.change_karma(points)
        except Exception as exc:
            msg = str(exc)

        post_msg(channel, msg)


def main():
    try:
        count = 0
        while True:
            count += 1
            if count % SAVE_INTERVAL == 0:
                _save_cache()

            time.sleep(1)

            message = parse_next_msg()
            if not message:
                continue

            karma_changes = KARMA_ACTION.findall(message.text)
            if not karma_changes:
                continue

            logging.debug('karma changes: {}'.format(str(karma_changes)))
            _process_karma_changes(message, karma_changes)
    finally:
        logging.info('Script ended, saving karma cache to file')
        # making sure we store karma cache before exiting the script, see
        # https://stackoverflow.com/questions/3850261/doing-something-before-program-exit
        _save_cache()


if __name__ == '__main__':
    main()
