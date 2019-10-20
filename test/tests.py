import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from pathlib import Path

from bot import SLACK_CLIENT
from bot.db.karma_user import KarmaUser
from bot.slack import format_user_id, get_available_username

from test.slack_testdata import TEST_USERINFO

# Database mocks
@pytest.fixture(scope="session")
def engine():
    return create_engine(f"sqlite:///{Path().absolute() / 'karma_test.db'}")


@pytest.fixture(scope="session")
def tables(engine):
    KarmaUser.metadata.create_all(engine)
    yield
    KarmaUser.metadata.drop_all(engine)


@pytest.fixture
def empty_db_session(engine, tables):
    """ Returns an SQLAlchemy session, and after the test
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
def filled_db_session(engine, tables):
    """ Returns an SQLAlchemy session, and after the test
    tears down everything properly.
    """
    connection = engine.connect()
    # begin the nested transaction
    transaction = connection.begin()
    # use the connection with the already started transaction
    session = Session(bind=connection)

    users = [
        KarmaUser(user_id="ABC123", username="pybob", karma_points=392),
        KarmaUser(user_id="EFG123", username="Julian Sequeira", karma_points=123),
        KarmaUser(user_id="XYZ123", username="clamytoe", karma_points=420),
    ]
    session.bulk_save_objects(users)
    session.commit()

    yield session

    session.close()
    # roll back the broader transaction
    transaction.rollback()
    # put back the connection to the connection pool
    connection.close()


# Slack API mocks
@pytest.fixture
def mock_slack_rtm_read(monkeypatch):
    def mock_rtm_read(*args, **kwargs):
        return {"type": "message", "user": "ABC123", "text": "Hi everybody"}

    monkeypatch.setattr(SLACK_CLIENT, "rtm_read", mock_rtm_read)


@pytest.fixture
def mock_slack_api_call(monkeypatch):
    def mock_api_call(*args, **kwargs):
        if args[0] == "users.info":
            user_id = kwargs.get("user")
            return TEST_USERINFO[user_id]

    monkeypatch.setattr(SLACK_CLIENT, "api_call", mock_api_call)


# Testing
def test_slack_rtm_read(mock_slack_rtm_read):
    event = SLACK_CLIENT.rtm_read()
    assert event["type"] == "message"
    assert event["user"] == "ABC123"
    assert event["text"] == "Hi everybody"


@pytest.mark.parametrize(
    "test_user_id, expected",
    [("ABC123", "pybob"), ("EFG123", "Julian Sequeira"), ("XYZ123", "clamytoe")],
)
def test_lookup_username(filled_db_session, test_user_id, expected):
    karma_user = filled_db_session.query(KarmaUser).get(test_user_id)
    assert karma_user.username == expected


def test_parse_next_msg():
    pass


def test_parse_karma_change():
    pass


def test_change_karma():
    pass


def test_change_karma_exceptions():
    pass


def test_change_karma_bot_self():
    pass


@pytest.mark.parametrize(
    "test_user_id, expected", [("ABC123", "<@ABC123>"), ("<@ABC123>", "<@ABC123>")]
)
def test_format_user_id(test_user_id, expected):
    assert format_user_id(test_user_id) == expected


@pytest.mark.parametrize(
    "test_user_id, expected",
    [("ABC123", "pybob"), ("EFG123", "Julian Sequeira"), ("XYZ123", "clamytoe")],
)
def test_get_available_username(mock_slack_api_call, test_user_id, expected):
    user_info = SLACK_CLIENT.api_call("users.info", user=test_user_id)
    assert get_available_username(user_info) == expected
