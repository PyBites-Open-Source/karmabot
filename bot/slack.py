from collections import namedtuple
import logging
import os

from slackclient import SlackClient

from . import KARMA_BOT, SLACK_CLIENT, USERNAME_CACHE

# bot commands
from commands.add import add_command
from commands.age import pybites_age
from commands.doc import doc_command
from commands.help import create_commands_table
from commands.feed import get_pybites_last_entries
from commands.score import get_karma, top_karma
from commands.tip import get_random_tip
from commands.topchannels import get_recommended_channels
from commands.welcome import welcome_user
from commands.zen import import_this

Message = namedtuple('Message', 'giverid channel text')

GENERAL_CHANNEL = 'C4SFQJJ9Z'
ADMINS = ('U4RTDPKUH', 'U4TN52NG6', 'U4SJVFMEG')  # bob, julian, pybites
TEXT_FILTER_REPLIES = dict(zen='`import this`',
                           cheers=':beers:',
                           braces='`SyntaxError: not a chance`')

AUTOMATED_COMMANDS = dict(welcome=welcome_user)  # not manual
ADMIN_BOT_COMMANDS = dict(top_karma=top_karma)
PUBLIC_BOT_COMMANDS = dict(age=pybites_age,
                           add=add_command,
                           help=create_commands_table,
                           tip=get_random_tip,
                           topchannels=get_recommended_channels)
PRIVATE_BOT_COMMANDS = dict(feed=get_pybites_last_entries,  # takes up space
                            doc=doc_command,
                            help=create_commands_table,  # have everywhere
                            karma=get_karma,
                            )


def create_help_msg(is_admin):
    help_msg = []
    help_msg.append('\n1. Channel commands (format: `@karmabot command`)')
    help_msg.append(create_commands_table(PUBLIC_BOT_COMMANDS))
    help_msg.append('\n2. Message commands (DM `@karmabot` typing `command`)')
    help_msg.append(create_commands_table(PRIVATE_BOT_COMMANDS))
    if is_admin:
        help_msg.append('\n3. Admin only commands')
        help_msg.append(create_commands_table(ADMIN_BOT_COMMANDS))
    return '\n'.join(help_msg)


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
                          as_user=True,
                          unfurl_links=False,
                          unfurl_media=False)


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


def _get_cmd(text, private=True):
    if private:
        return text.split()[0].strip().lower()

    # bot command needs to have bot fist in msg
    if not text.strip('<>@').startswith((KARMA_BOT, 'karmabot')):
        return None

    # need at least a command after karmabot
    if text.strip().count(' ') < 1:
        return None

    # @karmabot blabla -> get blabla
    cmd = text.split()[1]

    # of course ignore karma points
    if cmd.startswith(('+', '-')):
        return None

    return cmd.strip().lower()


def perform_bot_cmd(msg, private=True):
    """Parses message and perform valid bot commands"""
    user = msg.get('user')
    userid = user and user.strip('<>@')
    is_admin = userid and userid in ADMINS

    channel = msg.get('channel')
    text = msg.get('text')

    command_set = private and PRIVATE_BOT_COMMANDS or PUBLIC_BOT_COMMANDS
    cmd = text and _get_cmd(text, private=private)

    if not cmd:
        return None

    if cmd == 'help':
        return create_help_msg(is_admin)

    command = command_set.get(cmd)
    if private and is_admin and cmd in ADMIN_BOT_COMMANDS:
        command = ADMIN_BOT_COMMANDS.get(cmd)

    if not command:
        return None

    kwargs = dict(user=lookup_username(user),
                  channel=channel,
                  text=text)
    return command(**kwargs)


def perform_text_replacements(text):
    """Replace first matching word in text with a little easter egg"""
    words = text.lower().split()
    strip_chars = '?!'
    matching_words = [word.strip(strip_chars) for word in words
                      if word.strip(strip_chars) in TEXT_FILTER_REPLIES]

    if not matching_words:
        return None

    match_word = matching_words[0]
    replace_word = TEXT_FILTER_REPLIES.get(match_word)
    return 'To _{}_ I say: {}'.format(match_word, replace_word)


def parse_next_msg():
    """Parse next message posted on slack for actions todo by bot"""
    msg = SLACK_CLIENT.rtm_read()
    if not msg:
        return None
    msg = msg[0]
    user = msg.get('user')
    channel = msg.get('channel')
    text = msg.get('text')

    # handle events first
    type_event = msg.get('type')
    # 1. if new channel auto-join bot
    if type_event == 'channel_created':
        bot_joins_new_channel(msg)
        return None

    # 2. if a new user joins send a welcome msg
    if type_event == 'team_join':
        # return the message to apply the karma change
        # https://api.slack.com/methods/users.info
        welcome_msg = AUTOMATED_COMMANDS['welcome'](user)  # new user joining
        post_msg(GENERAL_CHANNEL, welcome_msg)
        # return Message object to handle karma in main
        return Message(giverid=KARMA_BOT,
                       channel=GENERAL_CHANNEL,
                       text=welcome_msg)
    # end events

    # not sure but sometimes we get dicts?
    if (not isinstance(channel, str) or
       not isinstance(user, str) or
       not isinstance(text, str)):
        return None

    # ignore anything karma bot says!
    if user == KARMA_BOT:
        return None

    # text replacements on first matching word in text
    # TODO: maybe this should replace all instances in text message ...
    text_replace_output = text and perform_text_replacements(text)
    if text_replace_output:
        post_msg(channel, text_replace_output)

    # if we recognize a valid bot command post its output, done
    # DM's = channels start with a 'D' / channel can be dict?!
    private = channel and channel.startswith('D')
    cmd_output = perform_bot_cmd(msg, private)
    if cmd_output:
        post_msg(channel, cmd_output)
        return None

    if not channel or not text:
        return None

    return Message(giverid=user, channel=channel, text=text)
