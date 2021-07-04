import logging

import karmabot.bot as bot


def join_public_channels(**kwargs):
    """Makes the bot join all public channels he is not in yet"""
    response = bot.app.client.conversations_list(
        exclude_archived=True, types="public_channel"
    )
    if response["ok"]:
        public_channels = response["channels"]
    else:
        logging.error("Could not retrieve public channel list for init join")
        return

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
