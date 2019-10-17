import os
import sys

import sqlalchemy as sa
import sqlalchemy.ext.declarative as dec
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session

from bot.db.modelbase import SqlAlchemyBase

__factory = None


def global_init():
    global __factory

    if __factory:
        return

    db_user = "karmabot"
    db_password = "pwd1234"
    db_host = "localhost"
    db_port = 5432
    db_name = "karmabot"

    # db_user = os.environ.get("SLACK_KARMA_DB_USER")
    # db_password = os.environ.get("SLACK_KARMA_DB_PW")
    # db_host = os.environ.get("SLACK_KARMA_DB_HOST")
    # db_port = os.environ.get("SLACK_KARMA_DB_PORT")
    # db_name = os.environ.get("SLACK_KARMA_DB_NAME")

    conn_str = f"postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    print("Connecting to DB with {}".format(conn_str))

    engine = sa.create_engine(conn_str, echo=False)
    try:
        engine.connect()
    except sa.exc.OperationalError:
        raise Exception("DB connection failed.")

    __factory = orm.sessionmaker(bind=engine)

    from bot.db.slack_user import SlackUser

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
