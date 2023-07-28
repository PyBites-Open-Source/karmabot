from unittest.mock import patch

import pytest

from karmabot.bot import karma_action, reply_commands, reply_help, reply_special_words
from karmabot.commands.welcome import welcome_user
from karmabot.settings import KARMABOT_ID


def _fake_say(text, channel=None):
    print(text)


@pytest.mark.parametrize(
    "test_message, expected",
    [
        (
            {"text": "<@EFG123> +++", "user": "ABC123", "channel": "FAKE_CHANNEL"},
            "Julian Sequeira's karma increased to 125",
        ),
        (
            {"text": "<@XYZ123> +++++", "user": "ABC123", "channel": "FAKE_CHANNEL"},
            "clamytoe's karma increased to 424",
        ),
    ],
)
@pytest.mark.usefixtures("mock_filled_db_session", "save_transaction_disabled")
def test_karma_action(capfd, test_message, expected):
    karma_action(test_message, _fake_say)  # type: ignore
    out = capfd.readouterr()[0]
    assert out.strip() == expected


@pytest.mark.parametrize(
    "test_message, expected",
    [
        ({"text": "Cheers everybody"}, "To _cheers_ I say: :beers:"),
        ({"text": "What about zen?"}, "To _zen_ I say: `import this`"),
        (
            {"text": "Anyone likes braces, huh?"},
            "To _braces_ I say: `SyntaxError: not a chance`",
        ),
    ],
)
def test_reply_special_words(capfd, test_message, expected):
    reply_special_words(test_message, print)  # type: ignore
    out = capfd.readouterr()[0]
    assert out.strip() == expected


def test_reply_help(capfd):
    message = {
        "text": "<@ABC123> help",
        "user": "XYZ789",
        "channel_type": "public_channel",
    }

    def fake_print(text, channel):
        print(text)

    reply_help(message, fake_print)  # type: ignore
    out = capfd.readouterr()[0]
    assert "age" in out
    assert "Print PyBites age in days" in out


def test_reply_commands_admin():
    pass


def test_reply_commands_public():
    pass


def test_reply_commands_private():
    pass


@pytest.mark.parametrize(
    "test_message, expected",
    [
        (
            {
                "text": f"<@{KARMABOT_ID}> yada yada",
                "user": "FAKE_USER",
                "channel": "FAKE_CHANNEL",
                "channel_type": "public_channel",
            },
            'Sorry <@FAKE_USER>, there is no command "yada"',
        ),
    ],
)
def test_reply_commands_unknown(capfd, test_message, expected):
    reply_commands(test_message, print)  # type: ignore
    out = capfd.readouterr()[0]
    assert out.strip() == expected


@patch("karmabot.commands.welcome.choice")
def test_welcome_new_user(choice_mock):
    choice_mock.return_value = "What is your favorite Python module?"
    actual_msg = welcome_user("bob")
    expected_msg = """Welcome <@bob> ++!

        Introduce yourself in #general if you like ...
        - What do you use Python for?
        - What is your day job?
        - And: >>> random.choice(pybites_init_questions)
        What is your favorite Python module?

        Although you will meet some awesome folks here, you can also talk to me :)
        Type `help` here to get started ...

        Enjoy PyBites Slack and keep calm and code in Python!

        <@FAKE_ADMIN1>, <@FAKE_ADMIN2> and <@FAKE_ADMIN3>"""
    assert [line.lstrip() for line in actual_msg.strip().splitlines()] == [
        line.lstrip() for line in expected_msg.strip().splitlines()
    ]


def autojoin_new_channels():
    pass


def test_perform_command():
    pass


def test_create_commands_table():
    pass
