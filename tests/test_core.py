from karmabot.commands.welcome import welcome_user
from karmabot.settings import KARMABOT_ID, SLACK_CLIENT
from karmabot.slack import GENERAL_CHANNEL, parse_next_msg


# Testing
def test_slack_team_join(mock_slack_rtm_read_team_join, mock_slack_api_call):
    user_id = SLACK_CLIENT.rtm_read()[0].get("user")["id"]
    welcome_user(user_id)

    actual = parse_next_msg()

    assert actual.user_id == KARMABOT_ID
    assert actual.channel_id == GENERAL_CHANNEL
    assert user_id in actual.text
    assert "Introduce yourself in #general if you like" in actual.text


def test_slack_rtm_read(mock_slack_rtm_read_msg):
    event = SLACK_CLIENT.rtm_read()
    assert event[0]["type"] == "message"
    assert event[0]["user"] == "ABC123"
    assert event[0]["text"] == "Hi everybody"
