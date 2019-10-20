import logging
import os
import sys

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from bot.db.modelbase import SqlAlchemyBase

__factory = None

# Credentials
SLACK_KARMADB_USER = os.environ.get("SLACK_KARMADB_USER")
SLACK_KARMADB_PASSWORD = os.environ.get("SLACK_KARMADB_PASSWORD")
SLACK_KARMADB_HOST = os.environ.get("SLACK_KARMADB_HOST")
SLACK_KARMADB_PORT = os.environ.get("SLACK_KARMADB_PORT")
SLACK_KARMADB_NAME = os.environ.get("SLACK_KARMADB_NAME")


def global_init():
    """ Sets up connection to DB and initializes models """
    global __factory

    if __factory:
        return

    conn_str = (
        f"postgres://{SLACK_KARMADB_USER}:{SLACK_KARMADB_PASSWORD}@"
        f"{SLACK_KARMADB_HOST}:{SLACK_KARMADB_PORT}/{SLACK_KARMADB_NAME}"
    )
    print(f"Connecting to DB with {conn_str}")

    engine = sa.create_engine(conn_str, echo=False)
    try:
        engine.connect()
    except OperationalError as exc:
        logging.error("Database connection failed.")
        sys.exit(1)

    print(f"DB connection successful")
    __factory = orm.sessionmaker(bind=engine)

    # noinspection PyUnresolvedReferences
    import bot.db.karma_user

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
