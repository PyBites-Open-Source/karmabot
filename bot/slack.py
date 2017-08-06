from collections import namedtuple
import logging

from . import KARMA_BOT, SLACK_CLIENT, USERNAME_CACHE

Message = namedtuple('Message', 'giverid channel text')

def lookup_username(userid):
    user = userid.strip('<>@')
    username = USERNAME_CACHE.get(user)
    if not username:
        userinfo = SLACK_CLIENT.api_call("users.info", user=user)
        username = userinfo['user']['name']
        USERNAME_CACHE[user] = username
    return username


def post_msg(channel, text):
    logging.debug('posting to {}'.format(channel))
    logging.debug(text)
    SLACK_CLIENT.api_call("chat.postMessage",
                          channel=channel,
                          text=text,
                          as_user=True)


def parse_next_msg():
    msg = SLACK_CLIENT.rtm_read()
    if not msg:
        return None

    msg = msg[0]
    giverid = msg.get('user')

    # ignore anything karma bot says!
    if giverid == KARMA_BOT:
        return None

    channel = msg.get('channel')
    text = msg.get('text')

    if not channel or not text:
        return None

    return Message(giverid=giverid, channel=channel, text=text)
