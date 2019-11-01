from bot import SLACK_CLIENT
from collections import namedtuple
from typing import List, Dict
import logging
from datetime import datetime as dt
from math import exp

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

Channel = namedtuple('Channel', 'id name purpose num_members latest_ts')


def get_recommended_channels(**kwargs):
    """Show some of our Community's favorite channels you can join
    see https://api.slack.com/methods/channels.list as well as https://api.slack.com/methods/channels.info for API info
    """
    _, text = kwargs.get('user'), kwargs.get('text')
    potential_channels: Channel = []
    msg = MSG_BEGIN

    nr_channels = text.split()[2] if len(text.split()) >= 3 else DEFAULT_NR_CHANNELS
    if isinstance(nr_channels, str):
        nr_channels = int(nr_channels) if nr_channels.isnumeric() else DEFAULT_NR_CHANNELS


    # retrieve channel list
    response: Dict = SLACK_CLIENT.api_call('channels.list', exclude_archived=True, exclude_members=True)
    if not response['ok']:
        logging.error(f'Error for API call "channels.list": {response["error"]}')
        return "I am truly sorry but something went wrong ;("
    
    channels: List[Dict] = response['channels']
    
    # retrieve channel info for each channel in channel list
    # only consider channels that are not the general channel, that are not private and that have at least one message
    for channel in channels:
        channel_is_potential = channel['is_channel'] and not channel['is_general'] and not channel['is_private']

        if channel_is_potential:
            # we have to stick with channel.info, also it could be
            # that the latest message is a bot or join message
            # but channels.history is not allowed for bots.
            # However, it seems that in the future, Slack will update the bot permissions
            # see: https://api.slack.com/methods/channels.history
            response: Dict = SLACK_CLIENT.api_call('channels.info', channel=channel['id'])
            if not response['ok']:
                logging.error(f'Error for API call "channel.info": {response["error"]}')
                return "I am truly sorry but something went wrong ;("
            
            channel_info: Dict = response['channel']

            if channel_info.get('latest', None):
                potential_channels.append(Channel(channel['id'], channel['name'], channel_info['purpose']['value'], channel['num_members'], float(channel_info['latest']['ts'])))

    # now weight channels and return message
    potential_channels = sorted(potential_channels, key=calc_channel_score, reverse=True)

    for channel in potential_channels[:nr_channels]:
        msg += f'{LIST_ICON} #{channel.name} ({channel.num_members} members, {seconds_since_last_post(channel) / 3600:.0f} hour(s) since last post): {channel.purpose if channel.purpose else "<Invest today and get an awesome description!>"}\n'

    return msg


def calc_channel_score(channel: Channel):
    """simple calculation of a channels value
    the higher the number of members and the less the number of seconds since the last post the higher the channels score
    """
    num_members = channel.num_members
    time_delta_in_hours = seconds_since_last_post(channel) / 3600

    return num_members * (exp(-time_delta_in_hours))


def seconds_since_last_post(channel: Channel) -> float:
    """return the fraction of days since the last post in a channel
    """
    return (dt.now() - dt.fromtimestamp(channel.latest_ts)).seconds


if __name__ == '__main__':
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = get_recommended_channels(**kwargs)
    print(output)
