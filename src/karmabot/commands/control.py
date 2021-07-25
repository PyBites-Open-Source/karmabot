import logging
from typing import Dict, List

import karmabot.bot as bot
from karmabot.slack import get_user_id


def join_public_channels(**kwargs):
    """Makes the bot join all public channels he is not in yet"""
    response = bot.app.client.conversations_list(
        exclude_archived=True, types="public_channel"
    )
    if response["ok"]:
        public_channels = response["channels"]
    else:
        error = "Could not retrieve public channel list"
        logging.error(error)
        return error

    channels_joined = []
    for channel in public_channels:
        if not channel["is_member"]:  # only join channels you are not already in
            bot.app.client.conversations_join(channel=channel["id"])
            bot.app.client.chat_postMessage(
                text="Karmabot is here! :wave:", channel=channel["id"]
            )
            channels_joined.append(channel["name"])

    if channels_joined:
        channels_text = ",".join(channels_joined)
        return f"I joined the following public channels: {channels_text}"

    return "There were no new public channels to join!"


def your_id(**kwargs):
    """Shows the user id of karmabot"""
    message = kwargs.get("text", "")
    bot_slack_id = message.split()[0]
    bot_user_id = get_user_id(bot_slack_id)

    if bot_user_id:
        return f"My user id is: {bot_user_id}"

    return "Sorry could not retrieve my user id"


def general_channel_id(**kwargs):
    """Shows the channel id of the general channel"""
    response: Dict = bot.app.client.conversations_list(
        exclude_archived=True, types="public_channel"
    )

    if not response["ok"]:
        logging.error('Error for API call "channels.list": %s', response["error"])
        return "I am truly sorry but something went wrong ;("

    channels: List[Dict] = response["channels"]
    for channel in channels:
        if channel["is_general"]:
            general_id = channel["id"]
            return f"The general channel id is: {general_id}"

    return "Sorry, could not find the general channel id :("
