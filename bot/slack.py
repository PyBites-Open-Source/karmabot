import logging

from . import KARMA_BOT, SLACK_CLIENT, USERNAME_CACHE


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
    ret = None, None, None

    msg = SLACK_CLIENT.rtm_read()
    if not msg:
        return ret

    msg = msg[0]
    giverid = msg.get('user')

    # ignore anything karma bot says!
    if giverid == KARMA_BOT:
        return ret

    channel = msg.get('channel')
    text = msg.get('text')

    ret = channel, text, giverid
    return ret
