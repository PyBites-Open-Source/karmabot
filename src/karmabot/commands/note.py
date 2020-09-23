import datetime
import re
from typing import Callable, Dict, Union

from karmabot.db import db_session
from karmabot.db.karma_note import KarmaNote
from karmabot.db.karma_user import KarmaUser

NOTE_CMD_PATTERN = re.compile(r"note\s(\w+)\s?(.*)")
NOTE_COMMANDS: Dict[str, Callable] = {
    "add": lambda text_arg, user: _add_note(text_arg, user),
    "del": lambda text_arg, user: _del_note(text_arg, user),
    "list": lambda text_arg, user: _list_notes(text_arg, user),
    "default": lambda text_arg, user: f"Sorry {user.username}, your note command was not recognized. You can use {', '.join(NOTE_COMMANDS.keys())}.",
}


def note(**kwargs) -> Union[None, str]:
    """Allows the user to store and retrieve simple notes.

    - Syntax for adding a note: @karmabot note add <">my note<"> (note message can be in quotes)
    - Syntax for listing notes: @karmabot note list
    - Syntax for removing a note: @karmabote note del 1
    """

    id_arg = str(kwargs.get("user_id"))
    text_arg = str(kwargs.get("text"))
    user_id = id_arg.strip("<>@")

    # retrieve current user
    user = db_session.create_session().query(KarmaUser).get(user_id)
    note_cmd = _parse_note_cmd(text_arg)

    note_cmd_fnc = NOTE_COMMANDS.get(note_cmd, NOTE_COMMANDS["default"])

    return note_cmd_fnc(text_arg, user)


def _add_note(text_arg: str, user: KarmaUser) -> str:
    """ Adds a new note to the database for the given user """
    note_msg = _parse_note_cmd_argument(text_arg)
    if not note_msg:
        return (
            f"Sorry {user.username}, could not find a note in your message. "
            f"Please make sure you have surrounded your note with double or single quotes."
        )

    note = KarmaNote(
        user_id=user.user_id, timestamp=datetime.datetime.now(), note=note_msg
    )

    session = db_session.create_session()
    session.add(note)
    session.commit()

    return f"Hey {user.username}, you've just stored a note."


def _del_note(text_arg: str, user: KarmaUser) -> str:
    """ Deletes the note with the given note id """
    note_id = _parse_note_cmd_argument(text_arg)

    if not note_id:
        return f"Sorry {user.username}, it seems you did not provide a correct note id."

    session = db_session.create_session()
    row_count = session.query(KarmaNote).filter(KarmaNote.id == note_id).delete()
    session.commit()  # otherwise, the deletion is not performed

    if row_count:
        return f"Hey {user.username}, your note was successfully deleted."

    return f"Hey {user.username}, something went wrong, no record was deleted. Please ask an admin..."


def _list_notes(text_arg: str, user: KarmaUser) -> str:
    """ """
    notes = (
        db_session.create_session()
        .query(KarmaNote)
        .filter(KarmaNote.user_id == user.user_id)
        .all()
    )

    if not notes:
        return f"Sorry {user.username}, you don't have any notes so far! Just start adding notes via the 'note add' command."

    msg = ""
    for note in notes:
        msg += f"{note.id}. note from {note.timestamp.strftime('%Y-%m-%d, %H:%M')}: {note.note}.\n"

    return msg


def _parse_note_cmd(text_arg: str) -> str:
    note_cmd = ""

    match = NOTE_CMD_PATTERN.search(text_arg)
    if match:
        note_cmd = match.group(1).strip()

    return note_cmd


def _parse_note_cmd_argument(text_arg: str) -> str:
    """ Get note message from user input. """
    note_cmd_argument = ""

    match = NOTE_CMD_PATTERN.search(text_arg)
    if match:
        note_cmd_argument = match.group(2).strip("\"'")

    return note_cmd_argument
