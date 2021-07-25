import pytest

import karmabot.bot  # noqa
from karmabot.db.database import database
from karmabot.db.karma_user import KarmaUser
from karmabot.karma import Karma


def test_karma_user_repr(karma_users):
    assert (
        repr(karma_users[0])
        == "<KarmaUser> ID: ABC123 | Username: pybob | Karma-Points: 392"
    )


@pytest.mark.parametrize(
    "test_user_id, expected",
    [("ABC123", "pybob"), ("EFG123", "Julian Sequeira"), ("XYZ123", "clamytoe")],
)
@pytest.mark.usefixtures("mock_filled_db_session")
def test_lookup_username(test_user_id, expected):
    with database.session_manager() as session:
        karma_user = session.query(KarmaUser).get(test_user_id)
    assert karma_user.username == expected


@pytest.mark.usefixtures("mock_empty_db_session", "users_profile_get_fake_user")
def test_create_karma_user():
    karma = Karma("ABC123", "XYZ123", "CHANNEL42")
    assert karma.giver.username == "pybob"
    assert karma.receiver.username == "clamytoe"

    with database.session_manager() as session:
        first = session.query(KarmaUser).get("ABC123")
        second = session.query(KarmaUser).get("XYZ123")

    assert first.username == "pybob"
    assert second.username == "clamytoe"
