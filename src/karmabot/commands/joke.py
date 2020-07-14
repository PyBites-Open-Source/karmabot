from typing import Union

import pyjokes

import karmabot

PYJOKE_HREF = "<https://pyjok.es/|PyJoke>"


def joke(**kwargs) -> Union[str, None]:
    """Posts a random PyJoke in the public or private channel"""

    # TODO: slack._get_cmd needs improvemed parsing to consider text
    # after commandes: e.g. joke chuck

    id_arg, text_arg = kwargs.get("user_id"), kwargs.get("text")

    if id_arg is not None and text_arg is not None:
        user_id = karmabot.slack.format_user_id(str(id_arg))
        user_text = str(text_arg)
    else:
        return None

    choice = "all"
    if "chuck" in user_text.lower():
        choice = "chuck"
    if "neutral" in user_text.lower():
        choice = "neutral"

    joke_text = pyjokes.get_joke(category=choice)

    return f"Hey {user_id}, here is a {PYJOKE_HREF} for you: _{joke_text}_"


if __name__ == "__main__":

    output = joke(user_id=123, text="42")
    print(output)

    output = joke(user_id=123, text="chuck")
    print(output)

    output = joke(user_id=123, text="neutral")
    print(output)
