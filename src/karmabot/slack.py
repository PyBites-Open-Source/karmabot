import logging
import os
import unicodedata
from collections import namedtuple
from typing import Union

from slack_bolt import App

# Commands
from karmabot.commands.add import add_command
from karmabot.commands.age import pybites_age
from karmabot.commands.doc import doc_command
from karmabot.commands.feed import get_pybites_last_entries
from karmabot.commands.help import create_commands_table
from karmabot.commands.joke import joke
from karmabot.commands.note import note
from karmabot.commands.score import get_karma, top_karma
from karmabot.commands.tip import get_random_tip
from karmabot.commands.topchannels import get_recommended_channels
from karmabot.commands.update_username import get_user_name, update_username
from karmabot.commands.welcome import welcome_user
from karmabot.karma import process_karma_changes

# Settings
from karmabot.settings import (
    ADMINS,
    GENERAL_CHANNEL,
    KARMA_ACTION,
    KARMABOT_ID,
    SLACK_BOT_TOKEN,
    SLACK_ID_FORMAT,
)

# constants
TEXT_FILTER_REPLIES = {
    "zen": "`import this`",
    "cheers": ":beers:",
    "braces": "`SyntaxError: not a chance`",
}

AUTOMATED_COMMANDS = {"welcome": welcome_user}  # not manual
ADMIN_BOT_COMMANDS = {"top_karma": top_karma}
PUBLIC_BOT_COMMANDS = {
    "add": add_command,
    "age": pybites_age,
    "help": create_commands_table,
    "joke": joke,
    "note": note,
    "tip": get_random_tip,
    "topchannels": get_recommended_channels,
}
PRIVATE_BOT_COMMANDS = {
    "doc": doc_command,
    "feed": get_pybites_last_entries,
    "help": create_commands_table,
    "joke": joke,
    "note": note,
    "karma": get_karma,
    "topchannels": get_recommended_channels,
    "username": get_user_name,
    "updateusername": update_username,
}

# Init
bot = App(token=SLACK_BOT_TOKEN)  # type: ignore


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


def get_available_username(user_profile):
    """
    Determines the username based on information available from slack.
    First information is used in the following order:
    1) display_name, 2) real_name, 3) name
    :param user_profile: Slack user_profile dict
    :return: human-readable username
    """

    display_name = user_profile["display_name_normalized"]
    if display_name:
        return display_name

    real_name = user_profile["real_name_normalized"]
    if real_name:
        return real_name


def get_channel_name(channel_id: str) -> str:
    channel_info: dict = (
        {}
    )  # TODO SLACK_CLIENT.api_call("channels.info", channel=channel_id)

    # Private channels and direct messages cannot be resolved via api
    if not channel_info["ok"]:
        return "Unknown or Private"

    channel_name = channel_info["channel"]["name"]
    return channel_name


# Maybe https://api.slack.com/methods/conversations.join
def bot_joins_new_channel(channel_id: str) -> None:
    text = (
        "Awesome, a new PyBites channel! Birds of a feather flock together! "
        "Keep doing your nerdy stuff, I will keep track of your karmas :)"
    )


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

    # def parse_next_msg():
    """Parse next message posted on slack for actions to do by bot"""
    msg = "TODO"  # TODO SLACK_CLIENT.rtm_read()
    if not msg:
        return None

    msg = msg[0]
    user_id = msg.get("user")
    channel_id = msg.get("channel")
    text = msg.get("text")

    logging.info(f"Parsing message {text} in channel {channel_id} from user {user_id}.")

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


@bot.message(KARMA_ACTION)  # type: ignore
def karma_action(message):
    msg = unicodedata.normalize("NFKD", message["text"])

    karma_giver = message["user"]
    channel_id = message["channel"]
    karma_changes = KARMA_ACTION.findall(msg)

    process_karma_changes(karma_giver, channel_id, karma_changes)


@bot.message(f"<@{KARMABOT_ID}> joke")  # type: ignore
def tell_joke(message, say):
    text = message["text"]
    user_id = message["user"]
    response_text = joke(user_id=user_id, text=text)

    say(response_text)


@bot.event("message")  # type: ignore
def handle_message_events(body, logger):
    logger.info(body)
