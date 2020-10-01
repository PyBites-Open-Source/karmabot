import pytest

from karmabot.db import db_session
from karmabot.db.karma_user import KarmaUser
from karmabot.karma import Karma
from karmabot.settings import SLACK_CLIENT
from karmabot.slack import format_user_id, get_available_username


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
