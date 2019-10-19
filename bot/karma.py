from . import IS_USER, MAX_POINTS, KARMABOT_ID
from .slack import lookup_username, post_msg

from .db import db_session
from .db.slack_user import SlackUser


def get_user_karma(user_id: str) -> int:
    """
    Retrieve karma points from database
    :param user_id: slack_id like ABC1234XYZ
    :return: number of user karma points
    """
    slack_id = user_id.strip("<>@")

    session = db_session.create_session()
    user: SlackUser = session.query(SlackUser).get(slack_id)

    try:
        return user.karma_points
    finally:
        session.close()


def _parse_karma_change(karma_change):
    user_id, voting = karma_change

    if IS_USER.match(user_id):
        receiver = user_id.strip("<>@")
    else:
        receiver = user_id.strip(" #").lower()  # ?

    points = voting.count("+") - voting.count("-")

    return receiver, points


def process_karma_changes(message, karma_changes):
    for karma_change in karma_changes:
        receiver_id, points = _parse_karma_change(karma_change)
        karma = Karma(giver_id=message.user_id, receiver_id=receiver_id)

        try:
            text = karma.change_karma(points)
        except Exception as exc:
            text = str(exc)

        post_msg(message.channel_id, text)


class Karma:
    def __init__(self, giver_id, receiver_id):
        self.giver_id = giver_id
        self.receiver_id = receiver_id
        self.giver_name = lookup_username(giver_id)
        self.receiver_name = lookup_username(receiver_id)
        self.last_score_maxed_out = False

    def _calc_final_score(self, points):
        if abs(points) > MAX_POINTS:
            self.last_score_maxed_out = True
            return MAX_POINTS if points > 0 else -MAX_POINTS
        else:
            self.last_score_maxed_out = False
            return points

    def _create_msg_bot_self_karma(self, points) -> str:
        receiver_karma = get_user_karma(self.receiver_id)
        if points > 0:
            text = (
                f"Thanks @{self.giver_name} for the extra karma"
                f", my karma is {receiver_karma} now."
            )
        else:
            text = (
                f"Not cool @{self.giver_name} lowering my karma to {receiver_karma},"
                f" but you are probably right, I will work harder next time."
            )
        return text

    def _create_msg(self, points):
        poses = "'" if self.receiver_name.endswith("s") else "'s"
        action = "increase" if points > 0 else "decrease"
        receiver_karma = get_user_karma(self.receiver_id)

        text = f"{self.receiver_name}{poses} karma {action}d to {receiver_karma}"
        if self.last_score_maxed_out:
            text += f" (= max {action} of {MAX_POINTS})"

        return text

    def change_karma(self, points):
        """ Updates Karma in the database """
        if not isinstance(points, int):
            err = (
                "Program bug: change_karma should "
                "not be called with a non int for "
                "points arg!"
            )
            raise RuntimeError(err)

        if self.giver_id == self.receiver_id:
            raise ValueError("Sorry, cannot give karma to self")

        points = self._calc_final_score(points)

        session = db_session.create_session()
        receiver = session.query(SlackUser).get(self.receiver_id)

        receiver.karma_points += points
        session.commit()
        session.close()

        if self.receiver_id == KARMABOT_ID:
            return self._create_msg_bot_self_karma(points)
        else:
            return self._create_msg(points)
