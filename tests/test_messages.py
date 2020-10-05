# Messages / Slack
import pytest

from karmabot.slack import perform_text_replacements


@pytest.mark.parametrize(
    "test_text, expected", [("Cheers everybody", "To _cheers_ I say: :beers:")]
)
def test_perform_text_replacements(test_text, expected):
    assert perform_text_replacements(test_text) == expected
