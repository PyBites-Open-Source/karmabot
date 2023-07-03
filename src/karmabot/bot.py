import logging
import re
import unicodedata
from typing import Callable, Dict

from slack_bolt import App

# Commands
from karmabot.commands.add import add_command
from karmabot.commands.age import pybites_age
from karmabot.commands.control import general_channel_id, join_public_channels, your_id
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
    KARMA_ACTION_PATTERN,
    KARMABOT_ID,
    SLACK_BOT_TOKEN,
    TEST_MODE,
)
from karmabot.slack import MessageChannelType

# command constants
ADMIN_BOT_COMMANDS = {
    "top_karma": top_karma,
    "join_public_channels": join_public_channels,
    "your_id": your_id,
    "general_channel_id": general_channel_id,
}
CHANNEL_BOT_COMMANDS = {
    "add": add_command,
    "age": pybites_age,
    "joke": joke,
    "note": note,
    "tip": get_random_tip,
    "topchannels": get_recommended_channels,
    "zen": import_this,
}
DM_BOT_COMMANDS = {
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

    full_commands = rf"^<@{KARMABOT_ID}>\s*({all_commands})(\s.*)?$"

    return re.compile(full_commands, re.IGNORECASE)


def compile_special_reply_pattern(replies: Dict[str, str]) -> re.Pattern:
    special_words = "|".join(replies.keys())
    pattern = rf"(?<!<@{KARMABOT_ID}>\s)({special_words})"
    return re.compile(pattern, flags=re.MULTILINE | re.IGNORECASE)


ADMIN_COMMAND_PATTERN = compile_command_pattern(ADMIN_BOT_COMMANDS)
CHANNEL_COMMAND_PATTERN = compile_command_pattern(CHANNEL_BOT_COMMANDS)
DM_COMMAND_PATTERN = compile_command_pattern(DM_BOT_COMMANDS)
UNKNOWN_COMMAND_PATTERN = re.compile(rf"^<@{KARMABOT_ID}>\s(\w*)")
HELP_COMMAND_PATTERN = re.compile(rf"^<@{KARMABOT_ID}>\s(help|commands)")
SPECIAL_WORDS_PATTERN = compile_special_reply_pattern(SPECIAL_REPLIES)
COMMAND_ERROR = "Sorry, something went wrong when performing the requested command"

# Slack Bolt App Init
# For testing we disable the token_verification, such that no valied token is required
TOKEN_VERIFICATION = not TEST_MODE
app = App(
    token=SLACK_BOT_TOKEN,
    name="Karmabot",
    token_verification_enabled=TOKEN_VERIFICATION,
)  # type: ignore


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
            f"{name:<30}: {func.__doc__.strip()}"
            for name, func in sorted(commands.items())
        ]
    )
    return f"```{ret}```"


# Top priority: process karma
@app.message(KARMA_ACTION_PATTERN)  # type: ignore
def karma_action(message, say):
    msg = unicodedata.normalize("NFKD", message["text"])

    karma_giver = message["user"]
    channel_id = message["channel"]
    karma_changes = KARMA_ACTION_PATTERN.findall(msg)

    karma_replies = process_karma_changes(karma_giver, channel_id, karma_changes)

    reply = "\n\n".join(karma_replies)
    say(reply)


# Help
@app.message(HELP_COMMAND_PATTERN)  # type: ignore
def reply_help(message, say):
    """Sends the list of available commands as DM to the user"""
    user_id = message["user"]
    channel_type = message["channel_type"]

    help_msg = [
        "\n1. Channel commands (format: `@karmabot command`)",
        create_commands_table(CHANNEL_BOT_COMMANDS),
        "\n2. Message commands (type `@karmabot command` in a DM to the bot)",
        create_commands_table(DM_BOT_COMMANDS),
    ]

    if user_id in ADMINS and channel_type == MessageChannelType.DM.value:
        help_msg.append("\n3. Admin only commands")
        help_msg.append(create_commands_table(ADMIN_BOT_COMMANDS))

    text = "\n".join(help_msg)
    say(text=text, channel=user_id)


# Message replies
@app.message(SPECIAL_WORDS_PATTERN)  # type: ignore
def reply_special_words(message, say):
    msg = message["text"].lower()
    special_word = SPECIAL_WORDS_PATTERN.findall(msg)[0]
    special_reply = SPECIAL_REPLIES.get(special_word)

    text = f"To _{special_word}_ I say: {special_reply}"

    say(text)


# Commands
@app.event("message")  # type: ignore
def reply_commands(message, say):  # noqa
    """
    Handles all the commands in one place

    Unfortunatly we cannot create sperate functions for every category
    (admin, private public) as some commands fit in multiple catagories and the
    first matching function would "swallow" the message and not forwared
    it further down the line
    """
    try:
        user_id = message["user"]
        channel_id = message["channel"]
        text = message["text"]
        channel_type = message["channel_type"]
    except KeyError as exc:
        logging.error("reply_commands error! Message was: %s", message, exc_info=exc)
        return

    kwargs = {"user_id": user_id, "channel": channel_id, "text": text}
    cmd_result = None

    admin_match = ADMIN_COMMAND_PATTERN.match(text)
    if (
        admin_match
        and channel_type == MessageChannelType.DM.value
        and user_id in ADMINS
    ):
        cmd_result = perform_command(ADMIN_BOT_COMMANDS, admin_match, kwargs)
        if not cmd_result:
            say(COMMAND_ERROR)
            raise CommandExecutionException(text)

    private_match = DM_COMMAND_PATTERN.match(text)
    if private_match and channel_type == MessageChannelType.DM.value:
        cmd_result = perform_command(DM_BOT_COMMANDS, private_match, kwargs)
        if not cmd_result:
            say(COMMAND_ERROR)
            raise CommandExecutionException(text)

    public_match = CHANNEL_COMMAND_PATTERN.match(text)
    if public_match and channel_type in [
        MessageChannelType.CHANNEL.value,
        MessageChannelType.GROUP.value,
    ]:
        cmd_result = perform_command(CHANNEL_BOT_COMMANDS, public_match, kwargs)
        if not cmd_result:
            say(COMMAND_ERROR)
            raise CommandExecutionException(text)

    if cmd_result:  # reply with result to a valid cmd
        say(cmd_result)
    elif UNKNOWN_COMMAND_PATTERN.match(text):  # everything else that looks like a cmd
        unknown_cmd = UNKNOWN_COMMAND_PATTERN.findall(text)[0]
        say(f'Sorry <@{user_id}>, there is no command "{unknown_cmd}"')

    # all other messages just do not get a reply


# Events
@app.event("team_join")  # type: ignore
def welcome_new_user(event, say):
    user_id = event["user"]["id"]
    text = welcome_user(user_id)
    logging.info("Sending welcome DM to new member %s", user_id)
    say(text=text, channel=user_id)


@app.event("channel_created")  # type: ignore
def autojoin_new_channels(event, say):
    new_channel_id = event["channel"]["id"]
    app.client.conversations_join(channel=new_channel_id)

    text = (
        "Awesome, a new PyBites channel! Birds of a feather flock together! "
        "Keep doing your nerdy stuff, I will keep track of your karmas :)"
    )
    say(text=text, channel=new_channel_id)
