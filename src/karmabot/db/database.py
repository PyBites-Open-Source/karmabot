import logging
import sys
from contextlib import contextmanager

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.exc import OperationalError

from karmabot import settings
from karmabot.db.modelbase import SqlAlchemyBase
from karmabot.exceptions import NotInitializedException


class Database:
    """Class for handlading the database connection and provide access to sessions"""

    def __init__(
        self, connection_string: str = settings.DATABASE_URL, echo: bool = False
    ) -> None:

        self.connection_string = connection_string
        self.echo = echo

        self._engine = None
        self._SessionFactory = None  # noqa

    def connect(self):
        """Sets up connection to DB and initializes models"""
        logging.debug("Connecting to DB with %s", self.connection_string)

        self._engine = sa.create_engine(self.connection_string, echo=self.echo)
        try:
            self._engine.connect()
        except OperationalError:
            logging.error("Database connection failed.")
            sys.exit(1)

        logging.info("DB connection successful")
        self._SessionFactory = orm.sessionmaker(bind=self.engine)

    def create_models(self):
        import karmabot.db.__all_models  # noqa: F401

        if not self._engine:
            raise NotInitializedException("SqlAlchemy engine is not initialized")
        SqlAlchemyBase.metadata.create_all(self._engine)

    @contextmanager
    def session_manager(self):
        if not self._SessionFactory:
            raise NotInitializedException("SessionFactory is not initialized")

        session = self._SessionFactory()

        try:
            yield session
        except Exception:
            logging.error("Rollback database transaction")
            session.rollback()
            raise
        finally:
            logging.debug("Closing database connection")
            session.close()

    @property
    def session(self):
        if not self._SessionFactory:
            raise NotInitializedException("SessionFactory is not initialized")
        return self._SessionFactory()

    @property
    def engine(self):
        if not self._engine:
            raise NotInitializedException("SqlAlchemy engine is not initialized")
        return self._engine


database = Database()
