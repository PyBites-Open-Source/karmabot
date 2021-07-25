from slack_bolt.adapter.socket_mode import SocketModeHandler

from karmabot.bot import app
from karmabot.db.database import database
from karmabot.settings import SLACK_APP_TOKEN


def main():
    database.connect()
    database.create_models()

    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()


if __name__ == "__main__":
    main()
