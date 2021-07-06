# Messages / Slack
import pytest

from karmabot.bot import karma_action, reply_commands, reply_help, reply_special_words
from karmabot.settings import KARMABOT_ID


@pytest.mark.parametrize(
    "test_message, expected",
    [
        ({"text": "<@EFG123> +++", "user": "ABC123", "channel": "FAKE_CHANNEL"}, "Julian Sequeira's karma increased to 125"),
        ({"text": "<@XYZ123> +++++", "user": "ABC123", "channel": "FAKE_CHANNEL"}, "clamytoe's karma increased to 424"),
    ]
)
def test_karma_action(mock_filled_db_session, save_transaction_disabled, capfd, test_message, expected):
    karma_action(test_message, print)  # type: ignore
    out, err = capfd.readouterr()
    assert out.strip() == expected


@pytest.mark.parametrize(
    "test_message, expected",
    [
        ({"text": "Cheers everybody"}, "To _cheers_ I say: :beers:"),
        ({"text": "What about zen?"}, "To _zen_ I say: `import this`"),
        ({"text": "Anyone likes braces, huh?"}, "To _braces_ I say: `SyntaxError: not a chance`")
    ]
)
def test_reply_special_words(capfd, test_message, expected):

    reply_special_words(test_message, print)  # type: ignore
    out, err = capfd.readouterr()
    assert out.strip() == expected


def test_reply_help(capfd):
    message = {
        "text": "<@ABC123> help",
        "user": "XYZ789",
        "channel_type": "public_channel",
    }

    reply_help(message, print)  # type: ignore
    out, err = capfd.readouterr()
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
    [({"text": f"<@{KARMABOT_ID}> yada yada",
       "user": "FAKE_USER",
       "channel": "FAKE_CHANNEL",
       "channel_type": "public_channel"},
      'Sorry <@FAKE_USER>, there is no command "yada"'),
     ],
)
def test_reply_commands_unknown(capfd, test_message, expected):
    reply_commands(test_message, print)  # type: ignore
    out, err = capfd.readouterr()
    assert out.strip() == expected


def test_welcome_new_user():
    pass


def autojoin_new_channels():
    pass


def test_perform_command():
    pass


def test_create_commands_table():
    pass
