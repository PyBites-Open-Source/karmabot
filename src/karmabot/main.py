import logging

from slack_bolt.adapter.socket_mode import SocketModeHandler

from karmabot.bot import bot
from karmabot.db import db_session
from karmabot.karma import process_karma_changes
from karmabot.settings import KARMA_ACTION, SLACK_APP_TOKEN
from karmabot.slack import check_connection


def main():
    # db_session.global_init()
    # check_connection()

    SocketModeHandler(
        bot,
        SLACK_APP_TOKEN,
    ).start()


@bot.event("message")
def karma(event, say):
    say("Is this karma?")
    msg = event["text"]

    karma_changes = KARMA_ACTION.findall(msg)
    if karma_changes:
        logging.info(f"Karma changes: {str(karma_changes)}")
        # TODO process_karma_changes(msg, karma_changes)
        say(f"uhh karma {karma_changes}")


if __name__ == "__main__":
    main()
