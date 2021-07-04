import pytest

from karmabot.db import db_session
from karmabot.db.karma_user import KarmaUser
from karmabot.karma import Karma, _parse_karma_change
from karmabot.settings import KARMA_ACTION_PATTERN, KARMABOT_ID


# Karma
@pytest.mark.parametrize(
    "test_message, expected",
    [
        ("<@ABC123> +++", ("<@ABC123>", "++")),
        ("Some cool text\nAnother line\n <@ABC123> +++", ("<@ABC123>", "++")),
        ("<@FOO42> ++++", ("<@FOO42>", "+++")),
        ("First line\n <@BAR789> ++++\n some more text after", ("<@BAR789>", "+++")),
    ],
)
def test_karma_regex(test_message, expected):
    karma_changes = KARMA_ACTION_PATTERN.findall(test_message)
    user_id, voting = karma_changes[0]

    assert user_id == expected[0]
    assert voting == expected[1]


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
