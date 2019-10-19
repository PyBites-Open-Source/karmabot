from bot.db.db_session import create_session
from bot.db.slack_user import SlackUser
from bot.slack import SLACK_CLIENT


def update_username(**kwargs):
    """Changes the Username"""
    slack_id = kwargs.get("user")

    session = create_session()
    slack_user: SlackUser = session.query(SlackUser).get(slack_id)

    if not slack_user:
        return "User not found"

    old_username = slack_user.username
    from bot.slack import get_available_username

    user_info = SLACK_CLIENT.api_call("users.info", user=slack_id)
    new_username = get_available_username(user_info)

    if old_username == new_username:
        return (
            f"Sorry, you have not updated your name: '{old_username}'. \n"
            "Please update your real or display name in your Slack profile and retry."
        )

    slack_user.username = new_username
    session.commit()
    session.close()
    return f"Sucessfully updated your name from '{old_username}' to '{new_username}'!"
