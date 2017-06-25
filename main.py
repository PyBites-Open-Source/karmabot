import logging
import pickle
import sys
import time

from bot.slack import post_msg, parse_next_msg
from bot.karma import parse_karma_change, change_karma

from bot import SLACK_CLIENT, KARMA_CACHE, KARMA_ACTION, karmas


def _end_script():
    # making sure we store karma cache before exiting the script, see
    # https://stackoverflow.com/questions/3850261/doing-something-before-program-exit
    logging.info('Script ended, saving karma cache to file')
    pickle.dump(karmas, open(KARMA_CACHE, "wb"))


def main():
    try:
        # Slack Real Time Messaging API - https://api.slack.com/rtm
        if not SLACK_CLIENT.rtm_connect():
            logging.error('Connection Failed, invalid token?')
            sys.exit(1)

        while True:
            time.sleep(1)

            channel, text, giverid = parse_next_msg()
            if not channel or not text or not giverid:
                continue

            karma_changes = KARMA_ACTION.findall(text)
            if not karma_changes:
                continue
            logging.debug('karma changes: {}'.format(str(karma_changes)))

            for kc in karma_changes:
                print(kc)
                userid, voting = kc
                giver, receiver, points = parse_karma_change(giverid,
                                                             userid,
                                                             voting)
                try:
                    msg = change_karma(giver, receiver, points)
                except ValueError as err:
                    msg = str(err)

                post_msg(channel, msg)
    finally:
        _end_script()


if __name__ == '__main__':
    main()
