from collections import namedtuple
import logging
import os
import random
from urllib.request import urlretrieve

from slackclient import SlackClient

from . import KARMA_BOT, SLACK_CLIENT, USERNAME_CACHE


# thanks Erik!
KARMA_BOT_HANDLE = '@karmabot'
WELCOME_MSG = """Welcome {user}++!

Introduce yourself if you like ...
- What do you use Python for?
- What is your day job?
- And: >>> random.choice(pybites_init_questions)
{welcome_question}

My creators are making me smarter, type this if you need anything
@karmabot help

Enjoy PyBites Slack and keep calm and code in Python!"""

FUNNY_QUESTIONS = 'http://projects.bobbelderbos.com/welcome_questions.txt'
FUNNY_QUESTIONS_TEMPFILE = os.path.join('/tmp', 'welcome_questions.txt')
GENERAL_CHANNEL = 'C4SFQJJ9Z'

Message = namedtuple('Message', 'giverid channel text')


def _get_bot_commands():
    commands_file = 'http://projects.bobbelderbos.com/bot_commands.txt'
    commands_tempfile = os.path.join('/tmp', 'bot_commands.txt')
    urlretrieve(commands_file, commands_tempfile)
    bot_commands = {}

    with open(commands_tempfile, encoding='utf8') as f:
        lines = f.readlines()[1:]
        cmd = None
        help_text = []

        for line in lines:
            if not line.strip():
                cmd = None
                continue

            if line.startswith('*'):
                cmd, cmd_str = line.strip('\n* ').split('|')
                bot_commands[cmd] = []
                help_text.append((cmd, cmd_str))
                continue

            bot_commands[cmd].append(line)

    bot_commands['help'] = '\n'.join(['{:<20}: {}'.format(cmd, cmd_str) for
                                      (cmd, cmd_str) in help_text])
    return bot_commands


BOT_COMMANDS = _get_bot_commands()


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


def perform_bot_cmd(text):
    """Parses message for valid bot command and returns output or None if
       not a valid bot command request"""
    if not text or not text.startswith(KARMA_BOT_HANDLE):
        return None

    if text.count(' ') < 1:
        return None

    cmd = text.split()[1]

    if cmd not in BOT_COMMANDS:
        return None

    return BOT_COMMANDS.get(cmd)


def _get_random_question():
    if not os.path.isfile(FUNNY_QUESTIONS_TEMPFILE):
        urlretrieve(FUNNY_QUESTIONS, FUNNY_QUESTIONS_TEMPFILE)

    with open(FUNNY_QUESTIONS_TEMPFILE, encoding='utf8') as f:
        questions = f.readlines()[1:]
        return random.choice(questions)


def _welcome_new_user(user):
    # https://api.slack.com/methods/users.info
    msg = WELCOME_MSG.format(user=user['name'],
                             welcome_question=_get_random_question())
    post_msg(GENERAL_CHANNEL, msg)
    return msg


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
    text = msg.get('text')

    # if we recognize a valid bot command post its output, done
    cmd_output = perform_bot_cmd(text)
    if cmd_output:
        post_msg(GENERAL_CHANNEL, cmd_output)
        return None

    # if a new user joins send a welcome msg
    if type_event == 'team_join':
        # return the message to apply the karma change
        text = _welcome_new_user(user)
        channel = GENERAL_CHANNEL
        user = KARMA_BOT

    if not channel or not text:
        return None

    return Message(giverid=user, channel=channel, text=text)
