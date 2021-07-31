import pytest

import karmabot.bot  # noqa
from karmabot.db.database import database
from karmabot.karma import Karma, KarmaUser, _parse_karma_change, process_karma_changes
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
    "giver, receiver, channel, amount",
    [
        ("ABC123", "XYZ123", "CHANNEL42", 2),
        ("XYZ123", "ABC123", "CHANNEL42", 5),
        ("EFG123", "ABC123", "CHANNEL42", -3),
    ],
)
@pytest.mark.usefixtures("conversations_info_fake_channel", "mock_filled_db_session")
def test_change_karma(giver, receiver, channel, amount):

    with database.session_manager() as session:
        pre_change_karma = session.query(KarmaUser).get(receiver).karma_points

    karma = Karma(giver, receiver, channel)
    karma.change_karma(amount)

    with database.session_manager() as session:
        post_change = session.query(KarmaUser).get(receiver).karma_points

    assert post_change == (pre_change_karma + amount)


@pytest.mark.usefixtures("save_transaction_disabled", "mock_filled_db_session")
def test_change_karma_msg():
    karma = Karma("ABC123", "XYZ123", "CHANNEL42")
    assert karma.change_karma(4) == "clamytoe's karma increased to 424"

    karma = Karma("EFG123", "ABC123", "CHANNEL42")
    assert karma.change_karma(-3) == "pybob's karma decreased to 389"


@pytest.mark.usefixtures("mock_filled_db_session")
def test_change_karma_exceptions(mock_filled_db_session):
    with pytest.raises(RuntimeError):
        karma = Karma("ABC123", "XYZ123", "CHANNEL42")
        karma.change_karma("ABC")

    with pytest.raises(ValueError):
        karma = Karma("ABC123", "ABC123", "CHANNEL42")
        karma.change_karma(2)


@pytest.mark.usefixtures("save_transaction_disabled", "mock_filled_db_session")
def test_change_karma_bot_self():
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


@pytest.mark.parametrize(
    "karma_giver, channel_id, karma_changes, expected",
    [
        (
            "ABC123",
            "FOO123",
            [("<@EFG123>", "++"), ("<@XYZ123>", "++")],
            [
                "Julian Sequeira's karma increased to 125",
                "clamytoe's karma increased to 422",
            ],
        ),
        (
            "XYZ123",
            "FOO123",
            [("<@ABC123>", "+++"), ("<@EFG123>", "++++")],
            [
                "pybob's karma increased to 395",
                "Julian Sequeira's karma increased to 127",
            ],
        ),
    ],
)
@pytest.mark.usefixtures("save_transaction_disabled", "mock_filled_db_session")
def test_process_karma_changes(karma_giver, channel_id, karma_changes, expected):
    karma_replies = process_karma_changes(karma_giver, channel_id, karma_changes)

    assert karma_replies == expected
