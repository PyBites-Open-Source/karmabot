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
DATABASE_URL = os.environ.get("DATABASE_URL")


def global_init():
    """ Sets up connection to DB and initializes models """
    global __factory

    if __factory:
        return

    print(f"Connecting to DB with {DATABASE_URL}")

    engine = sa.create_engine(DATABASE_URL, echo=False)
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
