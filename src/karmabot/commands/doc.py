"""A Karmabot pydoc interface.
"""
import contextlib
import io
import pydoc

import karmabot.slack

MSG_APOLOGY = """Sorry {username}, I got nothing for "{text}".

I'll do a keyword search for "{text}" if you add -k before {text}.

Try "topics" or "modules" for more general help.
"""

MSG_FOUNDIT = """Good news {username}, I found the following about {text}:
```
{result}
```
"""


MSG_HELP = """
pydoc [-k keyword] [module_path_or_topic|topics|modules|help]

You can use pydoc to look up all sorts of pythonic things!

Use this to get the docstring for a module:

    pydoc list

Or do a keyword search to get a list of modules that match:

    pydoc -k keyword

Get a list of modules:

    pydoc modules

A list of python language topics, super interesting:

    pydoc topics

And information about the specific listed topics:

    pydoc LOOPING

"""


def doc_command(**kwargs) -> str:
    """Browse and search python documentation, "pydoc help" """
    user_id = str(kwargs.get("user_id"))
    text = str(kwargs.get("text"))

    if len(text) == 0 or text.lower() == "help":
        return MSG_HELP

    apropos = "-k" in text

    if "-" in text and not apropos:  # weed out switches that aren't -k
        return MSG_HELP

    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        if apropos:
            pydoc.apropos(text.partition("-k")[-1])
        else:
            help(text)
    result = output.getvalue()

    slack_id = karmabot.slack.format_user_id(user_id)

    if result.startswith("No"):
        return MSG_APOLOGY.format(username=slack_id, text=text)

    return MSG_FOUNDIT.format(username=slack_id, text=text, result=result)


if __name__ == "__main__":
    import sys

    kwargs = {"user": "Erik", "channel": "#unix", "text": " ".join(sys.argv[1:])}
    print(doc_command(**kwargs))
