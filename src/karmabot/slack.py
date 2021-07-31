import re
from enum import Enum

SLACK_ID_PATTERN = re.compile(r"^<@[^>]+>$")


class MessageChannelType(Enum):
    DM = "im"
    CHANNEL = "channel"
    GROUP = "group"


def get_slack_id(user_id: str) -> str:
    """
    Formats a plain user_id (ABC123XYZ) to use slack identity
    Slack format <@ABC123XYZ> for highlighting users

    :param user_id: Plain user id
    :type user_id: str
    :return: Slack formatted user_id
    :rtype: str
    """
    if SLACK_ID_PATTERN.match(user_id):
        return user_id

    return f"<@{user_id}>"


def get_user_id(user_id: str) -> str:
    """
    Formats the user_id to a plain format removing any <, < or @
    :param user_id: slack id format
    :type user_id: str
    :return: plain user id
    :rtype: str
    """
    return user_id.strip("<>@")


def get_available_username(user_profile):
    """
    Determines the username based on information available from slack.
    First information is used in the following order:
    1) display_name, 2) real_name

    :param user_profile: Slack user_profile dict
    :return: human-readable username
    """

    display_name = user_profile["display_name_normalized"]
    if display_name:
        return display_name

    real_name = user_profile["real_name_normalized"]
    if real_name:
        return real_name

    raise ValueError("User Profile data missing name information")
