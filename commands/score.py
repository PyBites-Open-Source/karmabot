from bot.db import db_session
from bot.db.slack_user import SlackUser

TOP_NUMBER = 10


def get_karma(**kwargs):
    """Get your current karma score"""
    user_id = kwargs.get("user_id")
    slack_id = user_id.strip("<>@")

    session = db_session.create_session()
    su = session.query(SlackUser).get(slack_id)

    try:
        if not su:
            return "User not found"

        if su.karma_points == 0:
            return "Sorry, you don't have any karma yet"

        return f"Hey {su.username}, your current karma is {su.karma_points}"

    finally:
        session.close()


def top_karma(**kwargs):
    """Get the PyBites members with most karma"""
    output = ["PyBites members with most karma:"]

    session = db_session.create_session()
    top_users = (
        session.query(SlackUser)
        .order_by(SlackUser.karma_points.desc())
        .limit(TOP_NUMBER)
    )

    try:
        for top_user in top_users:
            output.append(
                "{:<20} -> {}".format(top_user.username, top_user.karma_points)
            )
        ret = "\n".join(output)
        return "```{}```".format(ret)

    finally:
        session.close()
