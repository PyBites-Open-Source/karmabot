import datetime
import re
from typing import Callable, Dict, Tuple, Union

from karmabot.db.database import database
from karmabot.db.karma_note import KarmaNote
from karmabot.db.karma_user import KarmaUser

NOTE_CMD_PATTERN = re.compile(r"note\s(\w+)\s?(.*)")


def note(user_id: str, channel: str, text: str) -> Union[None, str]:
    """Allows the user to store and retrieve simple notes.

    - Syntax for adding a note: @karmabot note add <">my note<"> (note message can be in quotes)
    - Syntax for listing notes: @karmabot note list
    - Syntax for removing a note: @karmabote note del 1

    Each note is stored for the current user only. A user can only list and delete her own notes.
    """
    user_id = user_id.strip("<>@")

    # retrieve current user
    with database.session_manager() as session:
        user = session.query(KarmaUser).get(user_id)

    cmd, _ = _parse_note_cmd(text)

    note_cmd_fnc = NOTE_COMMANDS.get(cmd, _command_not_found)

    return note_cmd_fnc(text, user)


def _add_note(text: str, user: KarmaUser) -> str:
    """Adds a new note to the database for the given user."""
    _, note_msg = _parse_note_cmd(text)
    if not note_msg:
        return f"Sorry {user.username}, could not find a note in your message."

    if _note_exists(note_msg, user):
        return f"Sorry {user.username}, you already have an identical note."

    note = KarmaNote(
        user_id=user.user_id, timestamp=datetime.datetime.now(), note=note_msg
    )

    with database.session_manager() as session:
        session.add(note)
        session.commit()

    return f"Hey {user.username}, you've just stored a note."


def _del_note(text: str, user: KarmaUser) -> str:
    """Deletes the note with the given note id."""
    _, note_id = _parse_note_cmd(text)

    if not note_id:
        return f"Sorry {user.username}, it seems you did not provide a valid id."

    with database.session_manager() as session:
        query = session.query(KarmaNote).filter_by(id=note_id, user_id=user.user_id)

        row_count = query.delete()
        session.commit()  # otherwise, the deletion is not performed

    if row_count:
        return f"Hey {user.username}, your note was successfully deleted."

    return (
        f"Sorry {user.username}, something went wrong, no record was deleted. "
        f"Please ask an admin..."
    )


def _list_notes(text: str, user: KarmaUser) -> str:
    """List all notes for a given user."""
    notes = _get_notes_for_user(user)

    if not notes:
        return (
            f"Sorry {user.username}, you don't have any notes so far! "
            f"Just start adding notes via the 'note add' command."
        )

    msg = "\n".join(f"{i+1}. note {str(note)}" for i, note in enumerate(notes))

    return msg


def _command_not_found(text: str, user: KarmaUser) -> str:
    return (
        f"Sorry {user.username}, your note command was not recognized. "
        f"You can use {', '.join(NOTE_COMMANDS.keys())}."
    )


def _parse_note_cmd(text: str) -> Tuple[str, str]:
    note_cmd = ("", "")

    match = NOTE_CMD_PATTERN.search(text)
    if match:
        note_cmd = match.group(1).strip(), match.group(2).strip("\"'")

    return note_cmd


def _get_notes_for_user(user: KarmaUser) -> list:
    with database.session_manager() as session:
        notes = session.query(KarmaNote).filter_by(user_id=user.user_id).all()
    return notes


def _note_exists(msg: str, user: KarmaUser) -> bool:
    with database.session_manager() as session:
        selected_note = session.query(KarmaNote).filter_by(
            note=msg, user_id=user.user_id
        )
        note_exists = session.query(
            selected_note.exists()
        ).scalar()  # returns True or False
    return note_exists


NOTE_COMMANDS: Dict[str, Callable] = {
    "add": _add_note,
    "del": _del_note,
    "list": _list_notes,
}
