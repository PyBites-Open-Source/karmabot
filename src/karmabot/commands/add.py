from karmabot import slack

MSG = """Hey {username}, so you want to propose a new command eh?

Awesome! Here are the steps:
1. Karmabot repo: https://github.com/pybites/karmabot
2. Fork the repo, make your branch.
3. Add your command script under the commands/ subdirectory.
4. Open a PR of your branch against PyBites repo.
5. Bob/Julian/Community to approve and merge it in.

Here is a walk-through video:
https://www.youtube.com/watch?v=Yx9qYl6lmzM&t=2s

Thanks!
"""


def add_command(**kwargs):
    """Instructions how to propose a new bot command"""
    user_id = kwargs.get("user_id")
    if not user_id:
        return None

    slack_id = slack.format_user_id(user_id)
    return MSG.format(username=slack_id)
