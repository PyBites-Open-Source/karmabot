import karmabot.slack
from karmabot.db.database import database
from karmabot.db.karma_user import KarmaUser

TOP_NUMBER = 10


def get_karma(**kwargs):
    """Get your current karma score"""
    user_id = kwargs.get("user_id")
    slack_id = karmabot.slack.get_slack_id(user_id)

    with database.session_manager() as session:
        kama_user = session.query(KarmaUser).get(user_id)

    if not kama_user:
        return "User not found"

    if kama_user.karma_points == 0:
        return "Sorry, you don't have any karma yet"

    return f"Hey {slack_id}, your current karma is {kama_user.karma_points}"


def top_karma(**kwargs):
    """Get the PyBites members with most karma"""
    output = ["PyBites members with most karma:"]

    with database.session_manager() as session:
        top_users = (
            session.query(KarmaUser)
            .order_by(KarmaUser.karma_points.desc())
            .limit(TOP_NUMBER)
        )

    if top_users:
        for top_user in top_users:
            output.append(f"{top_user.username:<20} -> {top_user.karma_points}")
        ret = "\n".join(output)
        return f"```{ret}```"

    return "Sorry, no users found"
