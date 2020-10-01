import os
from datetime import datetime
from unittest.mock import patch

import pytest
from slackclient import SlackClient as RealSlackClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import karmabot.commands.topchannels
from karmabot.commands.joke import _get_closest_category
from karmabot.commands.topchannels import Channel, calc_channel_score
from karmabot.commands.welcome import welcome_user
from karmabot.db import db_session
from karmabot.db.karma_note import KarmaNote
from karmabot.db.karma_transaction import KarmaTransaction
from karmabot.db.karma_user import KarmaUser
from karmabot.karma import Karma, _parse_karma_change
from karmabot.settings import KARMABOT_ID, SLACK_CLIENT
from karmabot.slack import (
    GENERAL_CHANNEL,
    format_user_id,
    get_available_username,
    parse_next_msg,
    perform_text_replacements,
)
from tests.slack_testdata import TEST_CHANNEL_HISTORY, TEST_CHANNEL_INFO, TEST_USERINFO

FAKE_NOW = datetime(2017, 8, 23)


@pytest.fixture
def frozen_now(monkeypatch):
    class PatchedDatetime(datetime):
        @classmethod
        def now(cls, **kwargs):
            return FAKE_NOW

    monkeypatch.setattr(karmabot.commands.topchannels, "dt", PatchedDatetime)


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

    monkeypatch.setattr(RealSlackClient, "rtm_read", mock_rtm_read)


@pytest.fixture
def mock_slack_rtm_read_team_join(monkeypatch):
    def mock_rtm_read(*args, **kwargs):
        return [{"type": "team_join", "user": {"id": "ABC123", "name": "bob"}}]

    monkeypatch.setattr(RealSlackClient, "rtm_read", mock_rtm_read)


@pytest.fixture
def mock_slack_api_call(monkeypatch):
    def mock_api_call(*args, **kwargs):
        call_type = args[1]

        if call_type == "users.info":
            user_id = kwargs.get("user")
            return TEST_USERINFO[user_id]

        if call_type == "channels.info":
            channel_id = kwargs.get("channel")
            return TEST_CHANNEL_INFO[channel_id]

        if call_type == "channels.history":
            channel_id = kwargs.get("channel")
            return TEST_CHANNEL_HISTORY[channel_id]

        if call_type == "chat.postMessage":
            return None

    monkeypatch.setattr(RealSlackClient, "api_call", mock_api_call)


# Testing
def test_slack_team_join(mock_slack_rtm_read_team_join, mock_slack_api_call):
    user_id = SLACK_CLIENT.rtm_read()[0].get("user")["id"]
    welcome_user(user_id)

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
def test_lookup_username(mock_filled_db_session, test_user_id, expected):
    karma_user = db_session.create_session().query(KarmaUser).get(test_user_id)
    assert karma_user.username == expected


def test_create_karma_user(mock_empty_db_session, mock_slack_api_call):
    karma = Karma("ABC123", "XYZ123", "CHANNEL42")
    assert karma.giver.username == "pybob"
    assert karma.receiver.username == "clamytoe"

    first = db_session.create_session().query(KarmaUser).get("ABC123")
    second = db_session.create_session().query(KarmaUser).get("XYZ123")

    assert first.username == "pybob"
    assert second.username == "clamytoe"


# KarmaNote
def test_karma_note_add(mock_filled_db_session):
    karmabot.commands.note.note(
        user_id="ABC123", channel="", text="note add my first note"
    )

    notes = db_session.create_session().query(KarmaNote).all()

    assert len(notes) == 1

    note = notes[0]

    assert note.id == 1
    assert note.user_id == "ABC123"
    assert note.timestamp is not None
    assert note.note == "my first note"

    karmabot.commands.note.note(
        user_id="ABC123", channel="", text="note add 'my second note'"
    )

    notes = db_session.create_session().query(KarmaNote).all()

    assert len(notes) == 2

    note = notes[-1]

    assert note.note == "my second note"


def test_karma_note_list(mock_filled_db_session):
    output = karmabot.commands.note.note(user_id="ABC123", channel="", text="note list")

    assert isinstance(output, str)
    assert output.startswith("Sorry")

    karmabot.commands.note.note(
        user_id="ABC123", channel="", text="note add my first note"
    )

    output = karmabot.commands.note.note(user_id="ABC123", channel="", text="note list")
    note = db_session.create_session().query(KarmaNote).all()[0]

    assert isinstance(output, str)
    assert output.startswith(f"{note.id}. note")


def test_karma_note_del(mock_filled_db_session):
    notes = db_session.create_session().query(KarmaNote).all()

    assert len(notes) == 0

    karmabot.commands.note.note(
        user_id="ABC123", channel="", text="note add my first note"
    )

    notes = db_session.create_session().query(KarmaNote).all()
    note = notes[0]

    assert len(notes) == 1

    karmabot.commands.note.note(
        user_id="ABC123", channel="", text=f"note del {note.id}"
    )

    notes = db_session.create_session().query(KarmaNote).all()

    assert len(notes) == 0


def test_karma_note_add_twice(mock_filled_db_session):
    output = karmabot.commands.note.note(
        user_id="ABC123", channel="", text="note add my first note"
    )
    output = karmabot.commands.note.note(
        user_id="ABC123", channel="", text="note add my first note"
    )

    notes = db_session.create_session().query(KarmaNote).all()

    assert len(notes) == 1
    assert output.startswith("Sorry")


def test_karma_note_del_other_users_note(mock_filled_db_session):
    output = karmabot.commands.note.note(
        user_id="ABC123", channel="", text="note add my first note"
    )
    output = karmabot.commands.note.note(
        user_id="EFG123", channel="", text="note add my first note"
    )

    notes = db_session.create_session().query(KarmaNote).all()

    assert len(notes) == 2

    for note in notes:
        output = karmabot.commands.note.note(
            user_id="XYZ123", channel="", text=f"note del {note.id}"
        )

        assert output.startswith("Sorry")
        assert len(notes) == 2


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
    [
        ("ABC123", "XYZ123", "CHANNEL42", 2),
        ("XYZ123", "ABC123", "CHANNEL42", 5),
        ("EFG123", "ABC123", "CHANNEL42", -3),
    ],
)
def test_change_karma(mock_filled_db_session, test_changes, mock_slack_api_call):
    session = db_session.create_session()
    pre_change_karma = session.query(KarmaUser).get(test_changes[1]).karma_points

    karma = Karma(test_changes[0], test_changes[1], test_changes[2])
    karma.change_karma(test_changes[3])

    post_change = session.query(KarmaUser).get(test_changes[1]).karma_points
    assert post_change == (pre_change_karma + test_changes[3])
    session.close()


def test_change_karma_msg(mock_filled_db_session):
    karma = Karma("ABC123", "XYZ123", "CHANNEL42")
    assert karma.change_karma(4) == "clamytoe's karma increased to 424"

    karma = Karma("EFG123", "ABC123", "CHANNEL42")
    assert karma.change_karma(-3) == "pybob's karma decreased to 389"


def test_change_karma_exceptions(mock_filled_db_session):
    with pytest.raises(RuntimeError):
        karma = Karma("ABC123", "XYZ123", "CHANNEL42")
        karma.change_karma("ABC")

    with pytest.raises(ValueError):
        karma = Karma("ABC123", "ABC123", "CHANNEL42")
        karma.change_karma(2)


def test_change_karma_bot_self(mock_filled_db_session):
    karma = Karma("ABC123", KARMABOT_ID, "CHANNEL42")
    assert (
        karma.change_karma(2) == "Thanks pybob for the extra karma, my karma is 12 now"
    )

    karma = Karma("EFG123", KARMABOT_ID, "CHANNEL42")
    assert (
        karma.change_karma(3)
        == "Thanks Julian Sequeira for the extra karma, my karma is 15 now"
    )

    karma = Karma("ABC123", KARMABOT_ID, "CHANNEL42")
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


def _channel_score(channel):
    channel_info = channel["channel"]
    return calc_channel_score(
        Channel(
            channel_info["id"],
            channel_info["name"],
            channel_info["purpose"]["value"],
            len(channel_info["members"]),
            float(channel_info["latest"]["ts"]),
            channel_info["latest"].get("subtype"),
        )
    )


def test_channel_score(mock_slack_api_call, frozen_now):
    most_recent = SLACK_CLIENT.api_call("channels.info", channel="CHANNEL42")
    less_recent = SLACK_CLIENT.api_call("channels.info", channel="CHANNEL43")
    assert _channel_score(most_recent) > _channel_score(less_recent)


@patch.dict(os.environ, {"SLACK_KARMA_INVITE_USER_TOKEN": "xoxp-162..."})
@patch.dict(os.environ, {"SLACK_KARMA_BOTUSER": "U5Z6KGX4L"})
def test_ignore_message_subtypes(mock_slack_api_call, frozen_now):
    latest_ignored = SLACK_CLIENT.api_call("channels.info", channel="SOMEJOINS")
    all_ignored = SLACK_CLIENT.api_call("channels.info", channel="ONLYJOINS")
    assert _channel_score(latest_ignored) > 0
    assert _channel_score(all_ignored) == 0


@pytest.mark.parametrize(
    "user_category, expected",
    [
        ("all", "all"),
        ("neutral", "neutral"),
        ("chuck", "chuck"),
        ("", "all"),
        ("al", "all"),
        ("neutr", "neutral"),
        ("chuk", "chuck"),
        ("help", "all"),
    ],
)
def test_get_closest_category(user_category, expected):
    assert _get_closest_category(user_category) == expected
