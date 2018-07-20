from collections import namedtuple
import logging
import os
import random
from urllib.request import urlretrieve

from slackclient import SlackClient

from . import KARMA_BOT, SLACK_CLIENT, USERNAME_CACHE

# thanks Erik!
WELCOME_MSG = """Welcome {user}++! Introduce yourself if you like.
What do you use Python for? What is your day job?
{fun_question}"""
FUNNY_QUESTIONS = 'http://projects.bobbelderbos.com/funny_questions.txt'
FUNNY_QUESTIONS_TEMPFILE = os.path.join('/tmp', 'funny_questions.txt')

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


def bot_joins_new_channel(msg):
    '''Bots cannot autojoin channels, but there is a hack: create a user token:
       https://stackoverflow.com/a/44107313/1128469 and
       https://api.slack.com/custom-integrations/legacy-tokens'''
    new_channel = msg['channel']['id']

    grant_user_token = os.environ.get('SLACK_KARMA_INVITE_USER_TOKEN')
    if not grant_user_token:
        logging.info('cannot invite bot, no env SLACK_KARMA_INVITE_USER_TOKEN')
        return None

    sc = SlackClient(grant_user_token)
    sc.api_call('channels.invite',
                channel=new_channel,
                user=KARMA_BOT)

    msg = 'Awesome, a new PyBites channel! Birds of a feather flock together!'
    msg += ' Keep doing your nerdy stuff, I will keep track of your karmas :)'

    post_msg(new_channel, msg)


def _get_random_question():
    if not os.path.isfile(FUNNY_QUESTIONS_TEMPFILE):
        urlretrieve(FUNNY_QUESTIONS, FUNNY_QUESTIONS_TEMPFILE)

    with open(FUNNY_QUESTIONS_TEMPFILE) as f:
        questions = f.readlines()[1:]
        return random.choice(questions)


def _welcome_new_user(user, channel, msg):
    msg = WELCOME_MSG.format(user=user,
                             fun_question=_get_random_question())
    post_msg(channel, msg)


def parse_next_msg():
    msg = SLACK_CLIENT.rtm_read()
    if not msg:
        return None
    msg = msg[0]

    type_event = msg.get('type')
    if type_event == 'channel_created':
        bot_joins_new_channel(msg)
        return None

    user = msg.get('user')

    # ignore anything karma bot says!
    if user == KARMA_BOT:
        return None

    channel = msg.get('channel')

    # if a new user joins send a welcome msg
    if type_event == 'team_join':
        _welcome_new_user(user, channel, msg)
        return None

    text = msg.get('text')

    if not channel or not text:
        return None

    return Message(giverid=user, channel=channel, text=text)
