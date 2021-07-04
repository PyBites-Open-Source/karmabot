import logging

import karmabot.bot as bot
import karmabot.slack
from karmabot.db.db_session import create_session
from karmabot.db.karma_user import KarmaUser


def update_username(**kwargs):
    """Changes the Username"""
    user_id = kwargs.get("user_id")
    if user_id:
        user_id = user_id.strip("<>@")

    session = create_session()
    karma_user: KarmaUser = session.query(KarmaUser).get(user_id)

    if not karma_user:
        return "User not found"

    old_username = karma_user.username

    response = bot.app.client.users_profile_get(user=user_id)
    status = response.status_code

    if status != 200:
        logging.info(f"Cannot get user info for {user_id} - API error: {status}")
        return "Sorry, I could not retrieve your user information from the slack API :("

    user_profile = response.data["profile"]
    new_username = karmabot.slack.get_available_username(user_profile)

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
    user_id = kwargs.get("user_id")
    if user_id:
        user_id = user_id.strip("<>@")

    session = create_session()
    karma_user: KarmaUser = session.query(KarmaUser).get(user_id)

    if not karma_user:
        return "Sorry, you are not yet known to karmabot. Try to give some Karma! :)"
    username = karma_user.username
    session.close()

    return f"Your current username for karmabot is '{username}'"
