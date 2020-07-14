import karmabot.slack
from karmabot import settings
from karmabot.db.db_session import create_session
from karmabot.db.karma_user import KarmaUser


def update_username(**kwargs):
    """Changes the Username"""
    user_id = kwargs.get("user_id").strip("<>@")

    session = create_session()
    karma_user: KarmaUser = session.query(KarmaUser).get(user_id)

    if not karma_user:
        return "User not found"

    old_username = karma_user.username
    user_info = settings.SLACK_CLIENT.api_call("users.info", user=user_id)
    new_username = karmabot.slack.get_available_username(user_info)

    if old_username == new_username:
        return (
            f"Sorry, you have not updated your username: {old_username}. \n"
            "Please update your real-name or display-name in your Slack "
            "profile and retry."
        )

    karma_user.username = new_username
    session.commit()
    session.close()

    return (
        f"Sucessfully updated your KarmaUser name "
        f"from '{old_username}' to '{new_username}'!"
    )


def get_user_name(**kwargs):
    """Shows the current Username"""
    user_id = kwargs.get("user_id").strip("<>@")

    session = create_session()
    karma_user: KarmaUser = session.query(KarmaUser).get(user_id)

    if not karma_user:
        return "Sorry, you are not yet known to karmabot. Try to give some Karma! :)"
    username = karma_user.username
    session.close()

    return f"Your current username for karmabot is '{username}'"
