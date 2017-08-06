import logging
import pickle
import sys
import time

from bot import SLACK_CLIENT, KARMA_CACHE, KARMA_ACTION, karmas
from bot.slack import post_msg, parse_next_msg
from bot.karma import parse_karma_change, change_karma

SAVE_INTERVAL = 60

# Slack Real Time Messaging API - https://api.slack.com/rtm
if not SLACK_CLIENT.rtm_connect():
    logging.error('Connection Failed, invalid token?')
    sys.exit(1)


def _save_cache():
    pickle.dump(karmas, open(KARMA_CACHE, "wb"))


def _process_karma_changes(message, karma_changes):
    for kc in karma_changes:
        userid, voting = kc
        giver, receiver, points = parse_karma_change(message.giverid,
                                                     userid,
                                                     voting)
        try:
            karma_msg = change_karma(giver, receiver, points)
        except ValueError as err:
            karma_msg = str(err)

        post_msg(message.channel, karma_msg)


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
