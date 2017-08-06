from . import IS_USER, MAX_POINTS, karmas
from .slack import lookup_username


def parse_karma_change(userid, voting):
    if IS_USER.match(userid):
        receiver = lookup_username(userid)
    else:
        receiver = userid.strip(' #').lower()

    # ++ = +1 point, +++ = +2, etc
    # same for negative:
    # -- = -1 point, --- = -2 etc
    points = voting.count('+') - voting.count('-')

    return receiver, points


def _create_msg(receiver, points, gt_max):
    poses = "'" if receiver.endswith('s') else "'s"
    action = 'increase' if points > 0 else 'decrease'
    receiver_karma = karmas.get(receiver, 0)

    msg = '{}{} karma {}d to {}'.format(receiver,
                                        poses,
                                        action,
                                        receiver_karma)
    if gt_max:
        msg += ' (= max {} of {})'.format(action, MAX_POINTS)

    return msg


def change_karma(giver, receiver, points):
    if giver == receiver:
        raise ValueError('Sorry, cannot give karma to self')

    if not isinstance(points, int):
        err = ('Program bug: change_karma should '
               'not be called wiht a non int for '
               'points arg!')
        raise RuntimeError(err)

    gt_max = False
    if abs(points) > MAX_POINTS:
        gt_max = True
        points = MAX_POINTS if points > 0 else -MAX_POINTS

    karmas[receiver] += points

    return _create_msg(receiver, points, gt_max)
