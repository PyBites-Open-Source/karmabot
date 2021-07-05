# Messages / Slack
import pytest

from karmabot.bot import reply_commands, reply_help, reply_special_words


@pytest.mark.parametrize(
    "test_message, expected",
    [({"text": "Cheers everybody"}, "To _cheers_ I say: :beers:"),
     ({"text": "What about zen?"}, "To _zen_ I say: `import this`"),
     ({"text": "Anyone likes braces, huh?"}, "To _braces_ I say: `SyntaxError: not a chance`")
     ],
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


def test_reply_commands():
    pass


def test_welcome_new_user():
    pass


def autojoin_new_channels():
    pass
