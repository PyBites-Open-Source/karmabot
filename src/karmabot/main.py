from slack_bolt.adapter.socket_mode import SocketModeHandler

from karmabot.db import db_session
from karmabot.settings import SLACK_APP_TOKEN
from karmabot.slack import bot


def main():
    db_session.global_init()

    handler = SocketModeHandler(bot, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
