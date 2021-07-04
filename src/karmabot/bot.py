import logging
import re
import unicodedata
from typing import Callable, Dict

from slack_bolt import App

# Commands
from karmabot.commands.add import add_command
from karmabot.commands.age import pybites_age
from karmabot.commands.doc import doc_command
from karmabot.commands.feed import get_pybites_last_entries
from karmabot.commands.joke import joke
from karmabot.commands.note import note
from karmabot.commands.score import get_karma, top_karma
from karmabot.commands.tip import get_random_tip
from karmabot.commands.topchannels import get_recommended_channels
from karmabot.commands.update_username import get_user_name, update_username
from karmabot.commands.welcome import welcome_user
from karmabot.commands.zen import import_this
from karmabot.exceptions import CommandExecutionException
from karmabot.karma import process_karma_changes

# Settings
from karmabot.settings import (
    ADMINS,
    GENERAL_CHANNEL,
    KARMA_ACTION_PATTERN,
    KARMABOT_ID,
    SLACK_BOT_TOKEN,
)

# command constants
ADMIN_BOT_COMMANDS = {"top_karma": top_karma}
PUBLIC_BOT_COMMANDS = {
    "add": add_command,
    "age": pybites_age,
    "joke": joke,
    "note": note,
    "tip": get_random_tip,
    "topchannels": get_recommended_channels,
    "zen": import_this,
}
PRIVATE_BOT_COMMANDS = {
    "doc": doc_command,
    "feed": get_pybites_last_entries,
    "joke": joke,
    "note": note,
    "karma": get_karma,
    "topchannels": get_recommended_channels,
    "username": get_user_name,
    "updateusername": update_username,
}

# other constants
SPECIAL_REPLIES = {
    "zen": "`import this`",
    "cheers": ":beers:",
    "braces": "`SyntaxError: not a chance`",
}


def compile_command_pattern(commands: Dict[str, Callable]) -> re.Pattern:
    command_words = commands.keys()
    all_commands = "|".join(command_words)

    full_commands = fr"^<@{KARMABOT_ID}>\s*({all_commands})(\s.*)?$"

    return re.compile(full_commands)


def compile_special_reply_pattern(replies: Dict[str, str]) -> re.Pattern:
    special_words = '|'.join(replies.keys())
    pattern = fr"(?<!<@{KARMABOT_ID}>\s)({special_words})"
    return re.compile(pattern, re.MULTILINE)


ADMIN_COMMAND_PATTERN = compile_command_pattern(ADMIN_BOT_COMMANDS)
PUBLIC_COMMAND_PATTERN = compile_command_pattern(PUBLIC_BOT_COMMANDS)
PRIVATE_COMMAND_PATTERN = compile_command_pattern(PRIVATE_BOT_COMMANDS)
SPECIAL_WORDS_PATTERN = compile_special_reply_pattern(SPECIAL_REPLIES)
COMMAND_ERROR = "Sorry, something went wrong when performing the requested command"

# Init
app = App(token=SLACK_BOT_TOKEN)  # type: ignore


# Helpers
def perform_command(commands, cmd_match, params):
    cmd = cmd_match.group(1)
    try:
        return commands[cmd](**params)
    except KeyError:
        return f"No command '{cmd}' found"


def create_commands_table(commands):
    """Print this help text"""
    ret = "\n".join(
        [
            "{:<30}: {}".format(name, func.__doc__.strip())
            for name, func in sorted(commands.items())
        ]
    )
    return "```{}```".format(ret)


# Top priority: process karma
@app.message(KARMA_ACTION_PATTERN)  # type: ignore
def karma_action(message):
    msg = unicodedata.normalize("NFKD", message["text"])

    karma_giver = message["user"]
    channel_id = message["channel"]
    karma_changes = KARMA_ACTION_PATTERN.findall(msg)

    process_karma_changes(karma_giver, channel_id, karma_changes)


# Help
@app.message(f"<@{KARMABOT_ID}> help")  # type: ignore
def reply_help(message, say):
    user_id = message["user"]
    channel_type = message["channel_type"]

    help_msg = [
        "\n1. Channel commands (format: `@karmabot command`)",
        create_commands_table(PUBLIC_BOT_COMMANDS),
        "\n2. Message commands (type `@karmabot command` in a DM to the bot)",
        create_commands_table(PRIVATE_BOT_COMMANDS),
    ]

    if user_id in ADMINS and channel_type == "im":
        help_msg.append("\n3. Admin only commands")
        help_msg.append(create_commands_table(ADMIN_BOT_COMMANDS))

    text = "\n".join(help_msg)
    say(text)


# Message replies
@app.message(SPECIAL_WORDS_PATTERN)  # type: ignore
def reply_special_words(message, say):

    msg = message["text"]
    special_word = SPECIAL_WORDS_PATTERN.findall(msg)[0]
    special_reply = SPECIAL_REPLIES.get(special_word)

    text = f"To _{special_word}_ I say: {special_reply}"

    say(text)


# Commands
@app.event("message")  # type: ignore
def reply_commands(message, say):
    """
    Handles all the commands in one place

    Unfortunatly we cannot create one function for every category (admin, private public)
    as some commands reside in multiple catagories and the first matching function
    would "swallow" the message and not forwared it further down the line
    """
    user_id = message["user"]
    channel_id = message["channel"]
    text = message["text"]
    channel_type = message["channel_type"]

    kwargs = {"user_id": user_id, "channel": channel_id, "text": text}
    cmd_result = None

    admin_match = ADMIN_COMMAND_PATTERN.match(text)
    if admin_match and channel_type == "im" and user_id in ADMINS:
        cmd_result = perform_command(ADMIN_BOT_COMMANDS, admin_match, kwargs)
        if not cmd_result:
            say(COMMAND_ERROR)
            raise CommandExecutionException(text)

    private_match = PRIVATE_COMMAND_PATTERN.match(text)
    if private_match and channel_type == "im":
        cmd_result = perform_command(PRIVATE_BOT_COMMANDS, private_match, kwargs)
        if not cmd_result:
            say(COMMAND_ERROR)
            raise CommandExecutionException(text)

    public_match = PUBLIC_COMMAND_PATTERN.match(text)
    if public_match and channel_type == "channel":
        cmd_result = perform_command(PUBLIC_BOT_COMMANDS, public_match, kwargs)
        if not cmd_result:
            say(COMMAND_ERROR)
            raise CommandExecutionException(text)

    say(cmd_result)


# Events
@app.event("team_join")  # type: ignore
def welcome_new_user(event, say):
    user_id = event["user"]

    text = welcome_user(user_id)
    say(text=text, channel=GENERAL_CHANNEL)


@app.event("channel_created")  # type: ignore
def autojoin_new_channels(event, say):
    new_channel_id = event["channel"]["id"]
    app.client.conversations_join(channel=new_channel_id)

    text = (
        "Awesome, a new PyBites channel! Birds of a feather flock together! "
        "Keep doing your nerdy stuff, I will keep track of your karmas :)"
    )
    say(text=text, channel=new_channel_id)


# Handling everyting else
@app.event("message")  # type: ignore
def handle_message_events(body, logger):
    logger.info(body)
