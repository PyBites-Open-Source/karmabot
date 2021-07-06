from collections import namedtuple

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from karmabot.db.database import database
from karmabot.db.karma_note import KarmaNote
from karmabot.db.karma_transaction import KarmaTransaction
from karmabot.db.karma_user import KarmaUser
from karmabot.settings import KARMABOT_ID

USERS = {
    "ABC123": "pybob",
    "EFG123": "Julian Sequeira",
    "XYZ123": "clamytoe",
    KARMABOT_ID: "karmabot",
}
SlackResponse = namedtuple("SlackResponse", "status_code, data")


@pytest.fixture
def save_transaction_disabled(monkeypatch):
    def _disabled(*args):
        return

    monkeypatch.setattr("karmabot.karma.Karma._save_transaction", _disabled)


# @pytest.fixture
# def deactivate_slack_auth(monkeypatch):
#     def _disabled_auth(*args):
#         pass

#     monkeypatch.setattr("slack_bolt.App._init_middleware_list", _disabled_auth)


@pytest.fixture
def conversations_info_fake_channel(monkeypatch):
    def mock_conversation_info(channel):
        response = SlackResponse(
            status_code=200, data={"channel": {"name": f"{channel}"}}
        )
        return response

    monkeypatch.setattr(
        "karmabot.bot.app.client.conversations_info", mock_conversation_info
    )


@pytest.fixture
def users_profile_get_fake_user(monkeypatch):
    def mock_users_profile_get(user):
        name = USERS.get(user)
        profile = {"display_name_normalized": name, "real_name_normalized": name}
        response = SlackResponse(status_code=200, data={"profile": profile})
        return response

    monkeypatch.setattr(
        "karmabot.bot.app.client.users_profile_get", mock_users_profile_get
    )


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite://")


@pytest.fixture(scope="session")
def tables(engine):
    KarmaUser.metadata.create_all(engine)
    KarmaTransaction.metadata.create_all(engine)
    KarmaNote.metadata.create_all(engine)
    yield
    KarmaUser.metadata.drop_all(engine)
    KarmaTransaction.metadata.drop_all(engine)
    KarmaNote.metadata.drop_all(engine)


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
    def mock_session_factory(*args, **kwargs):
        return filled_db_session

    monkeypatch.setattr(database, "_SessionFactory", mock_session_factory)


@pytest.fixture
def mock_empty_db_session(monkeypatch, empty_db_session):
    def mock_session_factory(*args, **kwargs):
        return empty_db_session

    monkeypatch.setattr(database, "_SessionFactory", mock_session_factory)


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
