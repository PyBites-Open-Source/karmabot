import pytest

from karmabot.slack import get_available_username, get_slack_id, get_user_id


@pytest.mark.parametrize(
    "test_profile, expected",
    [
        ({"display_name_normalized": "pybob", "real_name_normalized": "Bob"}, "pybob"),
        (
            {
                "display_name_normalized": None,
                "real_name_normalized": "Julian Sequeira",
            },
            "Julian Sequeira",
        ),
    ],
)
def test_get_available_username(test_profile, expected):
    assert get_available_username(test_profile) == expected


def test_get_available_username_wrong_format():
    with pytest.raises(ValueError) as e:
        get_available_username(
            {"display_name_normalized": None, "real_name_normalized": None}
        )

    assert str(e.value) == "User Profile data missing name information"


@pytest.mark.parametrize(
    "test_id, expected",
    [
        ("ABC123", "<@ABC123>"),
        ("EFG123", "<@EFG123>"),
        ("<@XYZ123>", "<@XYZ123>"),
        ("<@ABC123>", "<@ABC123>"),
    ],
)
def test_get_slack_id(test_id, expected):
    assert get_slack_id(test_id) == expected


@pytest.mark.parametrize(
    "test_id, expected",
    [
        ("<@ABC123>", "ABC123"),
        ("<@EFG123>", "EFG123"),
        ("XYZ123", "XYZ123"),
        ("ABC123", "ABC123"),
        ("ABC<>@123", "ABC<>@123"),
    ],
)
def test_get_user_id(test_id, expected):
    assert get_user_id(test_id) == expected
