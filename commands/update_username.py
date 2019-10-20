from bot.db.db_session import create_session
from bot.db.karma_user import KarmaUser
import bot.slack


def update_username(**kwargs):
    """Changes the Username"""
    user_id = kwargs.get("user_id").strip("<>@")

    session = create_session()
    karma_user: KarmaUser = session.query(KarmaUser).get(user_id)

    if not karma_user:
        return "User not found"

    old_username = karma_user.username
    user_info = bot.slack.SLACK_CLIENT.api_call("users.info", user=user_id)
    new_username = bot.slack.get_available_username(user_info)

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
