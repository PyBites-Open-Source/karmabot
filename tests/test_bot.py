import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from bot import SLACK_CLIENT, KARMABOT_ID
from bot.db import db_session
from bot.db.karma_user import KarmaUser
from bot.karma import _parse_karma_change, Karma
from bot.slack import (
    format_user_id,
    get_available_username,
    perform_text_replacements,
    parse_next_msg,
    Message,
    GENERAL_CHANNEL,
)
from tests.slack_testdata import TEST_USERINFO


# Database mocks
from welcome import welcome_user


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite://")


@pytest.fixture(scope="session")
def tables(engine):
    KarmaUser.metadata.create_all(engine)
    yield
    KarmaUser.metadata.drop_all(engine)


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
    """ Returns an SQLAlchemy session, and after the tests
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
    """ Returns an SQLAlchemy session, and after the tests
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

    monkeypatch.setattr(db_session, "create_session", mock_create_session)


@pytest.fixture
def mock_empty_db_session(monkeypatch, empty_db_session):
    def mock_create_session(*args, **kwargs):
        return empty_db_session

    monkeypatch.setattr(db_session, "create_session", mock_create_session)


# Slack API mocks
# TODO: needs to consider multiple messages / types
@pytest.fixture
def mock_slack_rtm_read_msg(monkeypatch):
    def mock_rtm_read(*args, **kwargs):
        return [{"type": "message", "user": "ABC123", "text": "Hi everybody"}]

    monkeypatch.setattr(SLACK_CLIENT, "rtm_read", mock_rtm_read)


@pytest.fixture
def mock_slack_rtm_read_team_join(monkeypatch):
    def mock_rtm_read(*args, **kwargs):
        return [{"type": "team_join", "user": {"id": "ABC123", "name": "bob"}}]

    monkeypatch.setattr(SLACK_CLIENT, "rtm_read", mock_rtm_read)


@pytest.fixture
def mock_slack_api_call(monkeypatch):
    def mock_api_call(*args, **kwargs):
        if args[0] == "users.info":
            user_id = kwargs.get("user")
            return TEST_USERINFO[user_id]
        if args[0] == "chat.postMessage":
            return None

    monkeypatch.setattr(SLACK_CLIENT, "api_call", mock_api_call)


# Testing
def test_slack_team_join(mock_slack_rtm_read_team_join, mock_slack_api_call):
    user_id = SLACK_CLIENT.rtm_read()[0].get("user")["id"]
    welcome_text = welcome_user(user_id)

    actual = parse_next_msg()

    assert actual.user_id == KARMABOT_ID
    assert actual.channel_id == GENERAL_CHANNEL
    assert user_id in actual.text
    assert "Introduce yourself in #general if you like" in actual.text


def test_slack_rtm_read(mock_slack_rtm_read_msg):
    event = SLACK_CLIENT.rtm_read()
    assert event[0]["type"] == "message"
    assert event[0]["user"] == "ABC123"
    assert event[0]["text"] == "Hi everybody"


# KarmaUser
def test_karma_user_formatted_user_id(karma_users):
    assert karma_users[0].formatted_user_id() == "<@ABC123>"
    assert karma_users[1].formatted_user_id() == "<@EFG123>"
    assert karma_users[2].formatted_user_id() == "<@XYZ123>"


def test_karma_user_repr(karma_users):
    assert (
        repr(karma_users[0])
        == "<KarmaUser> ID: ABC123 | Username: pybob | Karma-Points: 392"
    )


@pytest.mark.parametrize(
    "test_user_id, expected",
    [("ABC123", "pybob"), ("EFG123", "Julian Sequeira"), ("XYZ123", "clamytoe")],
)
def test_lookup_username(filled_db_session, test_user_id, expected):
    karma_user = filled_db_session.query(KarmaUser).get(test_user_id)
    assert karma_user.username == expected


def test_create_karma_user(mock_empty_db_session, mock_slack_api_call):
    karma = Karma("ABC123", "XYZ123")
    assert karma.giver.username == "pybob"
    assert karma.receiver.username == "clamytoe"

    first = db_session.create_session().query(KarmaUser).get("ABC123")
    second = db_session.create_session().query(KarmaUser).get("XYZ123")

    assert first.username == "pybob"
    assert second.username == "clamytoe"


# Messages / Slack
def test_get_cmd():
    pass


def test_perform_bot_cmd():
    pass


def test_parse_next_msg():
    pass


def test_create_help_msg():
    pass


@pytest.mark.parametrize(
    "test_text, expected", [("Cheers everybody", "To _cheers_ I say: :beers:")]
)
def test_perform_text_replacements(test_text, expected):
    assert perform_text_replacements(test_text) == expected


# Karma
@pytest.mark.parametrize(
    "test_change, expected",
    [(("<@ABC123>", "+++"), ("ABC123", 3)), (("<@XYZ123>", "----"), ("XYZ123", -4))],
)
def test_parse_karma_change(test_change, expected):
    assert _parse_karma_change(test_change) == expected


@pytest.mark.parametrize(
    "test_changes",
    [("ABC123", "XYZ123", 2), ("XYZ123", "ABC123", 5), ("EFG123", "ABC123", -3)],
)
def test_change_karma(mock_filled_db_session, test_changes):
    session = db_session.create_session()
    pre_change_karma = session.query(KarmaUser).get(test_changes[1]).karma_points

    karma = Karma(test_changes[0], test_changes[1])
    karma.change_karma(test_changes[2])

    session.commit()
    post_change = session.query(KarmaUser).get(test_changes[1]).karma_points
    assert post_change == (pre_change_karma + test_changes[2])


def test_change_karma_msg(mock_filled_db_session):
    karma = Karma("ABC123", "XYZ123")
    assert karma.change_karma(4) == "clamytoe's karma increased to 424"

    karma = Karma("EFG123", "ABC123")
    assert karma.change_karma(-3) == "pybob's karma decreased to 389"


def test_change_karma_exceptions(mock_filled_db_session):
    with pytest.raises(RuntimeError):
        karma = Karma("ABC123", "XYZ123")
        karma.change_karma("ABC")

    with pytest.raises(ValueError):
        karma = Karma("ABC123", "ABC123")
        karma.change_karma(2)


def test_change_karma_bot_self(mock_filled_db_session):
    karma = Karma("ABC123", KARMABOT_ID)
    assert (
        karma.change_karma(2) == "Thanks pybob for the extra karma, my karma is 12 now"
    )

    karma = Karma("EFG123", KARMABOT_ID)
    assert (
        karma.change_karma(3)
        == "Thanks Julian Sequeira for the extra karma, my karma is 15 now"
    )

    karma = Karma("ABC123", KARMABOT_ID)
    assert (
        karma.change_karma(-3)
        == "Not cool pybob lowering my karma to 12, but you are probably right, I will work harder next time"
    )


def test_process_karma_changes():
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
