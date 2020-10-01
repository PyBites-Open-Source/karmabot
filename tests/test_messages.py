# Messages / Slack
import pytest

from karmabot.slack import perform_text_replacements


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
