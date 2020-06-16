import logging
import sys

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from karmabot import settings
from karmabot.db.modelbase import SqlAlchemyBase

__factory = None


def global_init():
    """ Sets up connection to DB and initializes models """
    global __factory

    if __factory:
        return

    print(f"Connecting to DB with {settings.DATABASE_URL}")

    engine = sa.create_engine(settings.DATABASE_URL, echo=False)
    try:
        engine.connect()
    except OperationalError:
        logging.error("Database connection failed.")
        sys.exit(1)

    print("DB connection successful")
    __factory = orm.sessionmaker(bind=engine)

    import karmabot.db.__all_models  # noqa: F401

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()  # type: ignore
