import difflib
from typing import Union

import pyjokes

import karmabot.slack as slack

PYJOKE_HREF = "<https://pyjok.es/|PyJoke>"
CATEGORIES = list(pyjokes.jokes_en.jokes_en.keys())


def joke(**kwargs) -> Union[str, None]:
    """Posts a random PyJoke in the public or private channel"""

    # TODO: slack._get_cmd needs improvemed parsing to consider text
    # after commandes: e.g. joke chuck

    id_arg, text_arg = kwargs.get("user_id"), kwargs.get("text")

    if id_arg is not None and text_arg is not None:
        user_id = slack.format_user_id(str(id_arg))
        user_text = str(text_arg).lower()

        user_category = user_text.split()[-1] if len(user_text.split()) > 3 else ""
        category = _get_closest_category(user_category)

    else:
        return None

    joke_text = pyjokes.get_joke(category=category)

    return f"Hey {user_id}, here is a {PYJOKE_HREF} for you: _{joke_text}_"


def _get_closest_category(input: str):
    category = difflib.get_close_matches(input, CATEGORIES)
    category = category[0] if category else "all"

    return category
