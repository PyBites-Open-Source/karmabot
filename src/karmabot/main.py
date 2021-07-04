from slack_bolt.adapter.socket_mode import SocketModeHandler

from karmabot.bot import app
from karmabot.db import db_session
from karmabot.settings import SLACK_APP_TOKEN


def main():
    db_session.global_init()

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
