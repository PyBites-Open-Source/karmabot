import pytest

from karmabot.commands.joke import _get_closest_category


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
