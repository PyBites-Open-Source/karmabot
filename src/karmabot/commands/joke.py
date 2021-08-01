import difflib
from typing import Union

import pyjokes

import karmabot.slack

PYJOKE_HREF = "<https://pyjok.es/|PyJoke>"
CATEGORIES = list(pyjokes.jokes_en.jokes_en.keys())


def joke(**kwargs) -> Union[str, None]:
    """Posts a random PyJoke in the public or private channel"""
    user_id, text = kwargs.get("user_id"), kwargs.get("text")

    if user_id is not None and text is not None:
        slack_id = karmabot.slack.get_slack_id(user_id)
        words = text.lower().split()

        user_category = words[-1] if len(words) > 2 else ""
        category = _get_closest_category(user_category)
    else:
        return None

    joke_text = pyjokes.get_joke(category=category)

    return f"Hey {slack_id}, here is a {PYJOKE_HREF} for you: _{joke_text}_"


def _get_closest_category(input_category: str):
    category = difflib.get_close_matches(input_category, CATEGORIES)
    category = category[0] if category else "all"

    return category
