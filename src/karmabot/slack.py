import logging
import os
import sys
from collections import namedtuple
from typing import Union

from slackclient import SlackClient

from karmabot.commands.add import add_command
from karmabot.commands.age import pybites_age
from karmabot.commands.doc import doc_command
from karmabot.commands.feed import get_pybites_last_entries
from karmabot.commands.help import create_commands_table
from karmabot.commands.joke import joke
from karmabot.commands.score import get_karma, top_karma
from karmabot.commands.tip import get_random_tip
from karmabot.commands.topchannels import get_recommended_channels
from karmabot.commands.update_username import get_user_name, update_username
from karmabot.commands.welcome import welcome_user
from karmabot.settings import SLACK_ID_FORMAT  # noqa: BLK100
from karmabot.settings import ADMINS, GENERAL_CHANNEL, KARMABOT_ID, SLACK_CLIENT

# constants
TEXT_FILTER_REPLIES = {
    "zen": "`import this`",
    "cheers": ":beers:",
    "braces": "`SyntaxError: not a chance`",
}

AUTOMATED_COMMANDS = {"welcome": welcome_user}  # not manual
ADMIN_BOT_COMMANDS = {"top_karma": top_karma}
PUBLIC_BOT_COMMANDS = {
    "age": pybites_age,
    "add": add_command,
    "help": create_commands_table,
    "tip": get_random_tip,
    "topchannels": get_recommended_channels,
    "joke": joke,
}
PRIVATE_BOT_COMMANDS = {
    "feed": get_pybites_last_entries,
    "doc": doc_command,
    "help": create_commands_table,
    "karma": get_karma,
    "updateusername": update_username,
    "username": get_user_name,
    "joke": joke,
}

Message = namedtuple("Message", "user_id channel_id text")


def check_connection():
    # Slack Real Time Messaging API - https://api.slack.com/rtm
    if not SLACK_CLIENT.rtm_connect():
        logging.error("Connection Failed, invalid token?")
        sys.exit(1)


def get_bot_id():
    BOT_NAME = "karmabot"

    api_call = SLACK_CLIENT.api_call("users.list")

    if not api_call.get("ok"):
        error = api_call.get("error", "none")
        print(f"Could not get users.list, error: {error}")
        sys.exit(1)

    users = api_call.get("members")
    for user in users:
        if "name" in user and user.get("name") == BOT_NAME:
            print(f"Bot ID for {user['name']} is {user.get('id')}")


def create_help_msg(is_admin):
    help_msg = [
        "\n1. Channel commands (format: `@karmabot command`)",
        create_commands_table(PUBLIC_BOT_COMMANDS),
        "\n2. Message commands (type `command` in a DM to bot)",
        create_commands_table(PRIVATE_BOT_COMMANDS),
    ]
    if is_admin:
        help_msg.append("\n3. Admin only commands")
        help_msg.append(create_commands_table(ADMIN_BOT_COMMANDS))
    return "\n".join(help_msg)


def format_user_id(user_id: str) -> str:
    """
    Formats a plain user_id (ABC123XYZ) to use slack identity
    Slack API format <@ABC123XYZ>
    https://api.slack.com/methods/users.identity
    :param user_id: Plain user id
    :return: Slack formatted user_id
    """
    if SLACK_ID_FORMAT.match(user_id):
        return user_id

    return f"<@{user_id}>"


def get_available_username(user_info):
    """
    Determines the username based on information available from slack.
    First information is used in the following order:
    1) display_name, 2) real_name, 3) name
    See: https://api.slack.com/types/user
    :param user_info: Slack user_info object
    :return: human-readable username
    """

    display_name = user_info["user"]["profile"]["display_name_normalized"]
    if display_name:
        return display_name

    real_name = user_info["user"]["profile"]["real_name_normalized"]
    if real_name:
        return real_name

    # real_name is required and should always be there
    # defaulting to name for safety
    return user_info["user"]["name"]


def get_channel_name(channel_id: str) -> str:
    channel_info: dict = SLACK_CLIENT.api_call("channels.info", channel=channel_id)

    # Private channels and direct messages cannot be resolved via api
    if not channel_info["ok"]:
        return "Unknown or Private"

    channel_name = channel_info["channel"]["name"]
    return channel_name


def post_msg(channel_or_user_id: str, text) -> None:
    logging.info(f"Posting to {channel_or_user_id}: {text}")
    SLACK_CLIENT.api_call(
        "chat.postMessage",
        channel=channel_or_user_id,
        text=text,
        link_names=True,  # convert # and @ in links
        as_user=True,
        unfurl_links=False,
        unfurl_media=False,
    )


def bot_joins_new_channel(channel_id: str) -> None:
    """Bots cannot autojoin channels, but there is a hack: create a user token:
       https://stackoverflow.com/a/44107313/1128469 and
       https://api.slack.com/custom-integrations/legacy-tokens"""
    grant_user_token = os.environ.get("SLACK_KARMA_INVITE_USER_TOKEN")
    if not grant_user_token:
        logging.info("Cannot invite bot, no env SLACK_KARMA_INVITE_USER_TOKEN")
        return None

    sc = SlackClient(grant_user_token)
    sc.api_call("channels.invite", channel=channel_id, user=KARMABOT_ID)

    text = (
        "Awesome, a new PyBites channel! Birds of a feather flock together! "
        "Keep doing your nerdy stuff, I will keep track of your karmas :)"
    )

    post_msg(channel_id, text)


def _get_cmd(text, private=True):
    if private:
        return text.split()[0].strip().lower()

    # bot command needs to have bot first in msg
    if not text.strip("<>@").startswith((KARMABOT_ID, "karmabot")):
        return None

    # need at least a command after karmabot
    if text.strip().count(" ") < 1:
        return None

    # @karmabot blabla -> get blabla
    cmd = text.split()[1]

    # of course ignore karma points
    if cmd.startswith(("+", "-")):
        return None

    return cmd.strip().lower()


def perform_bot_cmd(msg, private=True):
    """Parses message and perform valid bot commands"""
    user = msg.get("user")
    user_id = user and user.strip("<>@")  # Why is this needed?
    is_admin = user_id and user_id in ADMINS

    channel_id = msg.get("channel")
    text = msg.get("text")

    command_set = private and PRIVATE_BOT_COMMANDS or PUBLIC_BOT_COMMANDS
    cmd = text and _get_cmd(text, private=private)

    if not cmd:
        return None

    if cmd == "help":
        return create_help_msg(is_admin)

    command = command_set.get(cmd)
    if private and is_admin and cmd in ADMIN_BOT_COMMANDS:
        command = ADMIN_BOT_COMMANDS.get(cmd)

    if not command:
        return None

    kwargs = {"user_id": user_id, "channel": channel_id, "text": text}
    return command(**kwargs)


def perform_text_replacements(text: str) -> Union[str, None]:
    """Replace first matching word in text with a little easter egg"""
    words = text.lower().split()
    strip_chars = "?!"
    matching_words = [
        word.strip(strip_chars)
        for word in words
        if word.strip(strip_chars) in TEXT_FILTER_REPLIES
    ]

    if not matching_words:
        return None

    match_word = matching_words[0]
    replace_word = TEXT_FILTER_REPLIES.get(match_word)
    return f"To _{match_word}_ I say: {replace_word}"


def parse_next_msg():
    """Parse next message posted on slack for actions to do by bot"""
    msg = SLACK_CLIENT.rtm_read()
    if not msg:
        return None

    msg = msg[0]
    user_id = msg.get("user")
    channel_id = msg.get("channel")
    text = msg.get("text")

    # handle events first
    event_type = msg.get("type")
    # 1. if new channel auto-join bot
    if event_type == "channel_created":
        bot_joins_new_channel(msg["channel"]["id"])
        return None

    # 2. if a new user joins send a welcome msg
    if event_type == "team_join":
        # return the message to apply the karma change
        # https://api.slack.com/methods/users.info
        welcome_msg = AUTOMATED_COMMANDS["welcome"](user_id["id"])  # new user joining
        post_msg(user_id["id"], welcome_msg)
        # return Message object to handle karma in main
        return Message(
            user_id=KARMABOT_ID, channel_id=GENERAL_CHANNEL, text=welcome_msg
        )
    # end events

    # not sure but sometimes we get dicts?
    if (
        not isinstance(channel_id, str)
        or not isinstance(user_id, str)
        or not isinstance(text, str)
    ):
        return None

    # ignore anything karma bot says!
    if user_id == KARMABOT_ID:
        return None

    # text replacements on first matching word in text
    # TODO: maybe this should replace all instances in text message ...
    text_replace_output = text and perform_text_replacements(text)
    if text_replace_output:
        post_msg(channel_id, text_replace_output)

    # if we recognize a valid bot command post its output, done
    # DM's = channels start with a 'D' / channel can be dict?!
    private = channel_id and channel_id.startswith("D")
    cmd_output = perform_bot_cmd(msg, private)
    if cmd_output:
        post_msg(channel_id, cmd_output)
        return None

    if not channel_id or not text:
        return None

    # Returns a message for karma processing
    return Message(user_id=user_id, channel_id=channel_id, text=text)
