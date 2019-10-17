from . import IS_USER, MAX_POINTS, karmas
from .slack import lookup_username, post_msg

from .db import db_session
from .db.slack_user import SlackUser

KARMABOT = 'karmabot'


def _parse_karma_change(karma_change):
    userid, voting = karma_change

    if IS_USER.match(userid):
        receiver = userid.strip("<>@")
    else:
        receiver = userid.strip(' #').lower()  # ?

    points = voting.count('+') - voting.count('-')

    return receiver, points


def process_karma_changes(message, karma_changes):
    for karma_change in karma_changes:
        channel = message.channel

        receiverid, points = _parse_karma_change(karma_change)

        karma = Karma(message.giverid, receiverid)

        try:
            msg = karma.change_karma(points)
        except Exception as exc:
            msg = str(exc)

        post_msg(channel, msg)


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

    def _create_msg_bot_self_karma(self, points):
        receiver_karma = karmas.get(self.receiver, 0)
        if points > 0:
            msg = 'Thanks @{} for the extra karma'.format(self.giver_name)
            msg += ', my karma is {} now'.format(receiver_karma)  # TODO: let karmabot get his points from db
        else:
            msg = 'Not cool @{} lowering my karma to {}'.format(self.giver_name,
                                                                receiver_karma)
            msg += ', but you are probably right'
            msg += ', I will work harder next time'
        return msg

    def _create_msg(self, points):
        poses = "'" if self.receiver_name.endswith('s') else "'s"
        action = 'increase' if points > 0 else 'decrease'
        receiver_karma = karmas.get(self.receiver_id, 0)  # TODO: let points from db

        msg = '{}{} karma {}d to {}'.format(self.receiver_name,
                                            poses,
                                            action,
                                            receiver_karma)
        if self.last_score_maxed_out:
            msg += ' (= max {} of {})'.format(action, MAX_POINTS)

        return msg

    def change_karma(self, points):
        """ Updates Karma in the database """
        if not isinstance(points, int):
            err = ('Program bug: change_karma should '
                   'not be called with a non int for '
                   'points arg!')
            raise RuntimeError(err)

        if self.giver_id == self.receiver_id:
            raise ValueError('Sorry, cannot give karma to self')

        points = self._calc_final_score(points)

        session = db_session.create_session()
        receiver = session.query(SlackUser).get(self.receiver_id)

        receiver.karma_points += points
        session.commit()

        if self.receiver_name == KARMABOT:
            return self._create_msg_bot_self_karma(points)
        else:
            return self._create_msg(points)
