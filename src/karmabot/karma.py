import logging

from karmabot.db import db_session
from karmabot.db.karma_transaction import KarmaTransaction
from karmabot.db.karma_user import KarmaUser
from karmabot.settings import KARMABOT_ID, MAX_POINTS, SLACK_CLIENT, SLACK_ID_FORMAT
from karmabot.slack import get_available_username, get_channel_name, post_msg


class GetUserInfoException(Exception):
    pass


def _parse_karma_change(karma_change):
    user_id, voting = karma_change

    if SLACK_ID_FORMAT.match(user_id):
        receiver = user_id.strip("<>@")
    else:
        receiver = user_id.strip(" #").lower()  # ?

    points = voting.count("+") - voting.count("-")

    return receiver, points


def process_karma_changes(message, karma_changes):
    for karma_change in karma_changes:
        receiver_id, points = _parse_karma_change(karma_change)
        try:
            karma = Karma(
                giver_id=message.user_id,
                receiver_id=receiver_id,
                channel_id=message.channel_id,
            )
        except GetUserInfoException:
            return

        try:
            text = karma.change_karma(points)
        except Exception as exc:
            text = str(exc)

        post_msg(message.channel_id, text)


class Karma:
    def __init__(self, giver_id, receiver_id, channel_id):
        self.session = db_session.create_session()
        self.giver = self.session.query(KarmaUser).get(giver_id)
        self.receiver = self.session.query(KarmaUser).get(receiver_id)
        self.channel_id = channel_id
        self.last_score_maxed_out = False

        if not self.giver:
            self.giver = self._create_karma_user(giver_id)
        if not self.receiver:
            self.receiver = self._create_karma_user(receiver_id)

    def _create_karma_user(self, user_id):
        user_info = SLACK_CLIENT.api_call("users.info", user=user_id)

        error = user_info.get("error")
        if error is not None:
            logging.info(f"Cannot get user info for {user_id} - error: {error}")
            raise GetUserInfoException

        slack_id = user_info["user"]["id"]
        username = get_available_username(user_info)

        new_user = KarmaUser(user_id=slack_id, username=username)
        self.session.add(new_user)
        self.session.commit()

        logging.info(f"Created new KarmaUser: {repr(new_user)}")
        return new_user

    def _calc_final_score(self, points):
        if abs(points) > MAX_POINTS:
            self.last_score_maxed_out = True
            return MAX_POINTS if points > 0 else -MAX_POINTS
        else:
            self.last_score_maxed_out = False
            return points

    def _create_msg_bot_self_karma(self, points) -> str:
        if points > 0:
            text = (
                f"Thanks {self.giver.username} for the extra karma"
                f", my karma is {self.receiver.karma_points} now"
            )
        else:
            text = (
                f"Not cool {self.giver.username} lowering my karma "
                f"to {self.receiver.karma_points}, but you are probably"
                f" right, I will work harder next time"
            )
        return text

    def _create_msg(self, points):
        receiver_name = self.receiver.username

        poses = "'" if receiver_name.endswith("s") else "'s"
        action = "increase" if points > 0 else "decrease"

        text = (
            f"{receiver_name}{poses} karma {action}d to "
            f"{self.receiver.karma_points}"
        )
        if self.last_score_maxed_out:
            text += f" (= max {action} of {MAX_POINTS})"

        return text

    def _save_transaction(self, points):
        transaction = KarmaTransaction(
            giver_id=self.giver.user_id,
            receiver_id=self.receiver.user_id,
            channel=get_channel_name(self.channel_id),
            karma=points,
        )
        self.session.add(transaction)
        self.session.commit()

        finished_transaction = (
            self.session.query(KarmaTransaction)
            .order_by(KarmaTransaction.id.desc())
            .first()
        )
        logging.info(repr(finished_transaction))

    def change_karma(self, points):
        """ Updates Karma in the database """
        if not isinstance(points, int):
            err = (
                "Program bug: change_karma should "
                "not be called with a non int for "
                "points arg!"
            )
            raise RuntimeError(err)

        try:
            if self.receiver.user_id == self.giver.user_id:
                raise ValueError("Sorry, cannot give karma to self")

            points = self._calc_final_score(points)
            self.receiver.karma_points += points
            self.session.commit()

            self._save_transaction(points)

            if self.receiver.user_id == KARMABOT_ID:
                return self._create_msg_bot_self_karma(points)
            else:
                return self._create_msg(points)

        finally:
            logging.info(
                (
                    f"[Karmachange] {self.giver.user_id} to "
                    f"{self.receiver.user_id}: {points}"
                )
            )
            self.session.close()
