import os
from unittest.mock import patch

import pytest

from karmabot.commands.joke import _get_closest_category
from karmabot.commands.topchannels import Channel, calc_channel_score
from karmabot.settings import SLACK_CLIENT


def _channel_score(channel):
    channel_info = channel["channel"]
    return calc_channel_score(
        Channel(
            channel_info["id"],
            channel_info["name"],
            channel_info["purpose"]["value"],
            len(channel_info["members"]),
            float(channel_info["latest"]["ts"]),
            channel_info["latest"].get("subtype"),
        )
    )


def test_channel_score(mock_slack_api_call, frozen_now):
    most_recent = SLACK_CLIENT.api_call("channels.info", channel="CHANNEL42")
    less_recent = SLACK_CLIENT.api_call("channels.info", channel="CHANNEL43")
    assert _channel_score(most_recent) > _channel_score(less_recent)


@patch.dict(os.environ, {"SLACK_KARMA_INVITE_USER_TOKEN": "xoxp-162..."})
@patch.dict(os.environ, {"SLACK_KARMA_BOTUSER": "U5Z6KGX4L"})
def test_ignore_message_subtypes(mock_slack_api_call, frozen_now):
    latest_ignored = SLACK_CLIENT.api_call("channels.info", channel="SOMEJOINS")
    all_ignored = SLACK_CLIENT.api_call("channels.info", channel="ONLYJOINS")
    assert _channel_score(latest_ignored) > 0
    assert _channel_score(all_ignored) == 0


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
