import pyjokes

from bot import slack

PYJOKE_HREF = "<https://pyjok.es/|PyJoke>"


def joke(**kwargs) -> str:
    """Posts a random PyJoke in the public or private channel"""

    # TODO: slack._get_cmd needs improvemed parsing to consider text
    # after commandes: e.g. joke chuck

    user_id: str = slack.format_user_id(kwargs.get("user_id"))
    user_text: str = kwargs.get("text")

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
