import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from karmabot.db.database import database
from karmabot.db.karma_transaction import KarmaTransaction
from karmabot.db.karma_user import KarmaUser
from karmabot.settings import KARMABOT_ID

from .slack_testdata import TEST_CHANNEL_HISTORY, TEST_CHANNEL_INFO, TEST_USERINFO

FAKE_NOW = datetime.datetime(2017, 8, 23)


@pytest.fixture
def frozen_now(monkeypatch):
    class PatchedDatetime(datetime):
        @classmethod
        def now(cls, **kwargs):
            return FAKE_NOW

    monkeypatch.setattr("datetime.datetime", PatchedDatetime)

@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite://")


@pytest.fixture(scope="session")
def tables(engine):
    KarmaUser.metadata.create_all(engine)
    KarmaTransaction.metadata.create_all(engine)
    yield
    KarmaUser.metadata.drop_all(engine)
    KarmaTransaction.metadata.drop_all(engine)


@pytest.fixture
def karma_users():
    return [
        KarmaUser(user_id="ABC123", username="pybob", karma_points=392),
        KarmaUser(user_id="EFG123", username="Julian Sequeira", karma_points=123),
        KarmaUser(user_id="XYZ123", username="clamytoe", karma_points=420),
        KarmaUser(user_id=KARMABOT_ID, username="karmabot", karma_points=10),
    ]


@pytest.fixture
def empty_db_session(engine, tables):
    """Returns an SQLAlchemy session, and after the tests
    tears down everything properly.
    """
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture
def filled_db_session(engine, tables, karma_users):
    """Returns an SQLAlchemy session, and after the tests
    tears down everything properly.
    """
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    session.bulk_save_objects(karma_users)
    session.commit()

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


@pytest.fixture
def mock_filled_db_session(monkeypatch, filled_db_session):
    def mock_create_session(*args, **kwargs):
        return filled_db_session

    monkeypatch.setattr(database, "session", mock_create_session)


@pytest.fixture
def mock_empty_db_session(monkeypatch, empty_db_session):
    def mock_create_session(*args, **kwargs):
        return empty_db_session

    monkeypatch.setattr(database, "session", mock_create_session)


# Slack API mocks
# TODO: needs to consider multiple messages / types
# @pytest.fixture
# def mock_slack_rtm_read_msg(monkeypatch):
#     def mock_rtm_read(*args, **kwargs):
#         return [{"type": "message", "user": "ABC123", "text": "Hi everybody"}]

#     monkeypatch.setattr(RealSlackClient, "rtm_read", mock_rtm_read)


# @pytest.fixture
# def mock_slack_rtm_read_team_join(monkeypatch):
#     def mock_rtm_read(*args, **kwargs):
#         return [{"type": "team_join", "user": {"id": "ABC123", "name": "bob"}}]

#     monkeypatch.setattr(RealSlackClient, "rtm_read", mock_rtm_read)


# @pytest.fixture
# def mock_slack_api_call(monkeypatch):
#     def mock_api_call(*args, **kwargs):
#         call_type = args[1]

#         if call_type == "users.info":
#             user_id = kwargs.get("user")
#             return TEST_USERINFO[user_id]

#         if call_type == "channels.info":
#             channel_id = kwargs.get("channel")
#             return TEST_CHANNEL_INFO[channel_id]

#         if call_type == "channels.history":
#             channel_id = kwargs.get("channel")
#             return TEST_CHANNEL_HISTORY[channel_id]

#         if call_type == "chat.postMessage":
#             return None

#     monkeypatch.setattr(RealSlackClient, "api_call", mock_api_call)
