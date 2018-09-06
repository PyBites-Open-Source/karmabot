from collections import namedtuple
import logging
import os

from slackclient import SlackClient

from . import KARMA_BOT, SLACK_CLIENT, USERNAME_CACHE

# bot commands
from commands.add import add_command
from commands.feed import get_pybites_last_entries
from commands.hello import hello_user
from commands.score import get_karma, top_karma
from commands.topchannels import get_recommended_channels
from commands.welcome import welcome_user

GENERAL_CHANNEL = 'C4SFQJJ9Z'
TEXT_FILTER_REPLIES = dict(fetchbeer=':beer:',
                           cheers=':beers:',
                           zen='`import this`',
                           braces='braces?! `SyntaxError: not a chance`')

PRIVATE_BOT_COMMANDS = dict(welcome=welcome_user)
BOT_COMMANDS = dict(add=add_command,
                    feed=get_pybites_last_entries,
                    hello=hello_user,
                    karma=get_karma,
                    top_karma=top_karma,
                    topchannels=get_recommended_channels)
HELP_TEXT = '\n'.join(['{:<30}: {}'.format(name, func.__doc__)
                       for name, func in sorted(BOT_COMMANDS.items())])

Message = namedtuple('Message', 'giverid channel text')


def lookup_username(userid):
    user = userid.strip('<>@')
    username = USERNAME_CACHE.get(user)
    if not username:
        userinfo = SLACK_CLIENT.api_call("users.info", user=user)
        username = userinfo['user']['name']
        USERNAME_CACHE[user] = username
    return username


def post_msg(channel_or_user, text):
    logging.debug('posting to {}'.format(channel_or_user))
    logging.debug(text)
    SLACK_CLIENT.api_call("chat.postMessage",
                          channel=channel_or_user,
                          text=text,
                          link_names=True,  # convert # and @ in links
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


def perform_bot_cmd(msg):
    """Parses message for valid bot command and returns output or None if
       not a valid bot command request"""
    user = msg.get('user')
    channel = msg.get('channel')
    text = msg.get('text')

    # bot command needs to have bot fist in msg
    if not text.strip('<>@').startswith((KARMA_BOT, 'karmabot')):
        return None

    # need at least a command after karmabot
    if text.strip().count(' ') < 1:
        return None

    # @karmabot blabla -> get blabla
    cmd = text.split()[1].strip().lower()

    # of course ignore karma points
    if cmd.startswith(('+', '-')):
        return None

    if cmd not in BOT_COMMANDS:
        help_msg = ''
        if cmd != 'help':
            help_msg += '`raise ValueError` ... I am not that smart (yet), valid commands:\n\n'  # noqa E501
        help_msg += '{:<30}: {}\n'.format('help', 'Print this help message')
        help_msg += HELP_TEXT
        return help_msg

    kwargs = dict(user=lookup_username(user),
                  channel=channel,
                  text=text)
    return BOT_COMMANDS[cmd](**kwargs)


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

    # text replacements on first matching word in text
    words = text and text.lower().split()
    if words:
        matching_words = [word.strip('?!') for word in words
                          if word.strip('?!') in TEXT_FILTER_REPLIES]
        if matching_words:
            replacement_word = TEXT_FILTER_REPLIES.get(matching_words[0])
            post_msg(channel, replacement_word)

    # if we recognize a valid bot command post its output, done
    cmd_output = text and perform_bot_cmd(msg)
    if cmd_output:
        # post bot commands to the requesting user
        post_msg(user, cmd_output)
        return None

    # if a new user joins send a welcome msg
    if type_event == 'team_join':
        # return the message to apply the karma change
        # https://api.slack.com/methods/users.info
        channel = GENERAL_CHANNEL
        msg = PRIVATE_BOT_COMMANDS['welcome'](user)  # new user joining
        post_msg(channel, msg)
        text = msg  # make sure to get to Message for karma
        user = KARMA_BOT  # do this last for the karma giving

    if not channel or not text:
        return None

    return Message(giverid=user, channel=channel, text=text)
