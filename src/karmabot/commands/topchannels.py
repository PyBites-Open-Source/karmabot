import logging
from collections import namedtuple
from datetime import datetime as dt
from math import exp
from operator import itemgetter
from typing import Dict, List, Optional, Union

import humanize
from slack_sdk.errors import SlackApiError

import karmabot.bot as bot
from karmabot.settings import KARMABOT_ID

MSG_BEGIN = "Glad you asked, here are some channels our Community recommends (based on member count and activity):\n"
MSG_LINE = (
    "- #{channel} ({member_count} members, last post {time_since_last_post}): {purpose}"
)
DEFAULT_NR_CHANNELS = 7

Channel = namedtuple("Channel", "id name purpose num_members latest_ts latest_subtype")


def channel_is_potential(channel):
    is_channel = channel["is_channel"]
    is_member = channel["is_member"]
    is_general = channel["is_general"]
    is_private = channel["is_private"]
    return is_channel and is_member and not is_general and not is_private


def collect_channel_info(channel):
    channel_id = channel["id"]
    try:
        info_response: Dict = bot.app.client.conversations_info(
            channel=channel_id, include_num_members=True
        )
        if not info_response["ok"]:
            raise SlackApiError("converstation.info error", info_response)

        history_response: Dict = bot.app.client.conversations_history(
            channel=channel_id, limit=1
        )
        if not history_response["ok"]:
            raise SlackApiError("conversation.history error", history_response)

    except SlackApiError as exc:
        logging.error(exc)
        return "I am truly sorry but something went wrong ;("

    channel_info: Dict = info_response["channel"]
    channel_history: Dict = history_response["messages"][0]

    latest_ts = channel_history.get("ts")
    latest_type = channel_history.get("type")
    if latest_ts:
        info = Channel(
            channel["id"],
            channel["name"],
            channel_info["purpose"]["value"],
            channel_info["num_members"],
            float(latest_ts),
            latest_type,
        )
        return info

    return None


def get_recommended_channels(**kwargs):
    """Show some of our Community's favorite channels you can join"""
    text = kwargs.get("text")

    potential_channels: Channel = []
    msg = MSG_BEGIN

    if not text:
        nr_channels = DEFAULT_NR_CHANNELS
    else:
        nr_channels = text.split()[2] if len(text.split()) >= 3 else DEFAULT_NR_CHANNELS

    if isinstance(nr_channels, str):
        nr_channels = (
            int(nr_channels) if nr_channels.isnumeric() else DEFAULT_NR_CHANNELS
        )

    # retrieve channel list
    response: Dict = bot.app.client.conversations_list(
        exclude_archived=True, types="public_channel"
    )

    if not response["ok"]:
        logging.error('Error for API call "channels.list": %s', response["error"])
        return "I am truly sorry but something went wrong ;("

    channels: List[Dict] = response["channels"]

    # retrieve channel info for each channel in channel list
    # only consider channels that are not the general channel, that are not private and that have at least one message
    for channel in channels:
        if channel_is_potential(channel):
            info = collect_channel_info(channel)
            if info:
                potential_channels.append(info)

    # now weight channels and return message
    potential_channels = sorted(
        ((calc_channel_score(chan), chan) for chan in potential_channels), reverse=True
    )

    msg = MSG_BEGIN + "\n".join(
        (
            MSG_LINE.format(
                channel=channel.name,
                member_count=channel.num_members,
                time_since_last_post=humanize.naturaltime(
                    seconds_since_last_post(channel)
                ),
                purpose=channel.purpose
                or "<Invest today and get an awesome description!>",
            )
            for score, channel in potential_channels[:nr_channels]
            if score > 0
        )
    )

    return msg


def get_messages(
    channel: Channel, ignore_message_types: Union[set, None] = None
) -> Union[List[Dict], None]:
    """Return a list of the most recent messages in a given channel, filtering
    out certain message types.

    Similar to invite permissions, this requires a user token.

    "New" bot tokens will be both more granular and more flexible, so should
    be able to replace the need for user tokens going forward:

    Ref: https://api.slack.com/docs/token-types#bot_new
    """
    if ignore_message_types is None:
        ignore_message_types = {"channel_join"}

    response = bot.app.client.conversations_history(
        channel=channel.id, user=KARMABOT_ID
    )

    return response["messages"]


def calc_channel_score(channel: Channel):
    """simple calculation of a channels value
    the higher the number of members and the less the number of seconds since the last post the higher the channels score
    """
    since_latest = seconds_since_last_post(channel)
    if not since_latest:
        return 0
    num_members = channel.num_members
    time_delta_in_hours = since_latest / 3600

    return num_members * (exp(-time_delta_in_hours))


def seconds_since_last_post(channel: Channel) -> Optional[float]:
    """return the fraction of days since the last post in a channel, or None if
    all messages are of filtered/ignored subtypes
    """

    ignore_message_types = {"channel_join"}

    if channel.latest_subtype not in ignore_message_types:
        latest_ts = channel.latest_ts
    else:
        msgs = get_messages(channel, ignore_message_types)
        if not msgs:
            return None
        latest_ts = float(max(msgs, key=itemgetter("ts"))["ts"])

    return (dt.now() - dt.fromtimestamp(latest_ts)).total_seconds()
