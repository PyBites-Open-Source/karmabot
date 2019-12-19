import logging
import os
from collections import namedtuple
from datetime import datetime as dt
from math import exp
from operator import itemgetter
from typing import Dict, List, Optional

from slackclient import SlackClient

from bot.settings import SLACK_CLIENT

TOP_CHANNELS = """Glad you asked, here are some channels our Communtiy recommends:
- #100daysofcode: share your 100 days journey and/or feedback on our course
- #books: get notified about Packt's daily free ebook and/or share interesting books you are reading
- #codechallenges: stuck? Ask your Python coding questions here, we learn more together!
- #instagram: submit inspiring Python/coding/developer pictures for PyBites Instagram
- #meetups / #pycon: the PyBites community is growing so maybe you can meet fellow Pythonistas in person!
- #pybites-news: share interesting Python news/articles here helping us with our weekly Twitter news digest
- #checkins: share your pythonic adventures with the community and help everyone grow!
"""

MSG_BEGIN = "Glad you asked, here are some channels our Communtiy recommends (based on member count and activity):\n"
LIST_ICON = "-"
DEFAULT_NR_CHANNELS = 7

Channel = namedtuple("Channel", "id name purpose num_members latest_ts latest_subtype")


def get_recommended_channels(**kwargs):
    """Show some of our Community's favorite channels you can join
    see https://api.slack.com/methods/channels.list as well as https://api.slack.com/methods/channels.info for API info
    """
    _, text = kwargs.get("user"), kwargs.get("text")
    potential_channels: Channel = []
    msg = MSG_BEGIN

    nr_channels = text.split()[2] if len(text.split()) >= 3 else DEFAULT_NR_CHANNELS
    if isinstance(nr_channels, str):
        nr_channels = (
            int(nr_channels) if nr_channels.isnumeric() else DEFAULT_NR_CHANNELS
        )

    # retrieve channel list
    response: Dict = SLACK_CLIENT.api_call(
        "channels.list", exclude_archived=True, exclude_members=True
    )
    if not response["ok"]:
        logging.error(f'Error for API call "channels.list": {response["error"]}')
        return "I am truly sorry but something went wrong ;("

    channels: List[Dict] = response["channels"]

    # retrieve channel info for each channel in channel list
    # only consider channels that are not the general channel, that are not private and that have at least one message
    for channel in channels:
        channel_is_potential = (
            channel["is_channel"]
            and not channel["is_general"]
            and not channel["is_private"]
        )

        if channel_is_potential:
            # we have to stick with channel.info, also it could be
            # that the latest message is a bot or join message
            # but channels.history is not allowed for bots.
            # However, it seems that in the future, Slack will update the bot permissions
            # see: https://api.slack.com/methods/channels.history
            response: Dict = SLACK_CLIENT.api_call(
                "channels.info", channel=channel["id"]
            )
            if not response["ok"]:
                logging.error(f'Error for API call "channel.info": {response["error"]}')
                return "I am truly sorry but something went wrong ;("

            channel_info: Dict = response["channel"]

            if channel_info.get("latest", None):
                potential_channels.append(
                    Channel(
                        channel["id"],
                        channel["name"],
                        channel_info["purpose"]["value"],
                        channel["num_members"],
                        float(channel_info["latest"]["ts"]),
                        channel_info["latest"].get("subtype"),
                    )
                )

    # now weight channels and return message
    potential_channels = sorted(
        ((calc_channel_score(chan), chan) for chan in potential_channels), reverse=True
    )

    msg = MSG_BEGIN + "\n".join(
        (
            f'{LIST_ICON} #{channel.name} ({channel.num_members} members, {seconds_since_last_post(channel) / 3600:.0f} hour(s) since last post): {channel.purpose if channel.purpose else "<Invest today and get an awesome description!>"}'
            for score, channel in potential_channels[:nr_channels]
            if score > 0
        )
    )

    return msg


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
        # The latest message in this channel has an ignored subtype, so we need
        # to dig through history to find the most recent non-ignored message.
        # Similar to invite permissions, this requires a user token.
        #
        # "New" bot tokens will be both more granular and more flexible, so should
        # be able to replace the need for user tokens going forward:
        #
        # Ref: https://api.slack.com/docs/token-types#bot_new

        grant_user_token = os.environ.get("SLACK_KARMA_INVITE_USER_TOKEN")
        karmabot_id = os.environ.get("SLACK_KARMA_BOTUSER")
        if not grant_user_token:
            logging.info(
                "Cannot search channel history, no env SLACK_KARMA_INVITE_USER_TOKEN"
            )
            return None

        sc = SlackClient(grant_user_token)
        response = sc.api_call("channels.history", channel=channel.id, user=karmabot_id)

        msgs = [
            msg
            for msg in response["messages"]
            if msg.get("subtype") not in ignore_message_types
        ]
        if not msgs:
            return None
        latest_ts = float(max(msgs, key=itemgetter("ts"))["ts"])

    return (dt.now() - dt.fromtimestamp(latest_ts)).total_seconds()


if __name__ == "__main__":
    user, channel, text = "bob", "#general", "some message"
    kwargs = dict(user=user, channel=channel, text=text)
    output = get_recommended_channels(**kwargs)
    print(output)
