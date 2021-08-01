import logging

import karmabot.bot as bot
import karmabot.slack as slack
from karmabot.db.database import database
from karmabot.db.karma_transaction import KarmaTransaction
from karmabot.db.karma_user import KarmaUser
from karmabot.exceptions import GetUserInfoException
from karmabot.settings import KARMABOT_ID, MAX_POINTS


class Karma:
    def __init__(self, giver_id, receiver_id, channel_id):
        self.session = database.session
        self.giver: KarmaUser = self.session.query(KarmaUser).get(giver_id)
        self.receiver: KarmaUser = self.session.query(KarmaUser).get(receiver_id)

        if not self.giver:
            self.giver = self._create_karma_user(giver_id)
        if not self.receiver:
            self.receiver = self._create_karma_user(receiver_id)

        self.channel_id: str = channel_id
        self.last_score_maxed_out: bool = False

    def _create_karma_user(self, user_id):
        response = bot.app.client.users_profile_get(user=user_id)
        status = response.status_code

        if status != 200:
            logging.info("Cannot get user info for %s - API error: %s", user_id, status)
            raise GetUserInfoException

        user_profile = response.data["profile"]
        username = slack.get_available_username(user_profile)

        new_user = KarmaUser(user_id=user_id, username=username)
        self.session.add(new_user)
        self.session.commit()

        logging.info("Created new KarmaUser: %s", repr(new_user))
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

        response = bot.app.client.conversations_info(channel=self.channel_id)

        if response.status_code != 200:
            raise Exception(
                f"Slack API could not get Channel info - Status {response.status_code}"
            )

        channel_name = response.data["channel"]["name"]

        transaction = KarmaTransaction(
            giver_id=self.giver.user_id,
            receiver_id=self.receiver.user_id,
            channel=channel_name,
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
        """Updates Karma in the database"""
        if not isinstance(points, int):
            err = "change_karma should not be called with a non int points arg!"
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
                "[Karmachange] %s to %s: %s",
                self.giver.user_id,
                self.receiver.user_id,
                points,
            )
            self.session.close()


def _parse_karma_change(karma_change):
    user_id, voting = karma_change

    receiver = slack.get_user_id(user_id)
    points = voting.count("+") - voting.count("-")

    return receiver, points


def process_karma_changes(karma_giver, channel_id, karma_changes):
    messages = []
    for karma_change in karma_changes:
        receiver_id, points = _parse_karma_change(karma_change)
        try:
            karma = Karma(
                giver_id=karma_giver,
                receiver_id=receiver_id,
                channel_id=channel_id,
            )
        except GetUserInfoException:
            return "Sorry, something went wrong while retrieving user information"

        try:
            text = karma.change_karma(points)
        except (RuntimeError, ValueError) as exc:
            text = str(exc)

        messages.append(text)

    return messages
