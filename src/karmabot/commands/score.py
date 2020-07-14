from karmabot.db import db_session
from karmabot.db.karma_user import KarmaUser

TOP_NUMBER = 10


def get_karma(**kwargs):
    """Get your current karma score"""
    user_id = kwargs.get("user_id").strip("<>@")

    session = db_session.create_session()
    kama_user = session.query(KarmaUser).get(user_id)

    try:
        if not kama_user:
            return "User not found"

        if kama_user.karma_points == 0:
            return "Sorry, you don't have any karma yet"

        return (
            f"Hey {kama_user.username}, your current karma is {kama_user.karma_points}"
        )

    finally:
        session.close()


def top_karma(**kwargs):
    """Get the PyBites members with most karma"""
    output = ["PyBites members with most karma:"]

    session = db_session.create_session()
    top_users = (
        session.query(KarmaUser)
        .order_by(KarmaUser.karma_points.desc())
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
