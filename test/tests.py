import os
from nose.tools import assert_raises
from unittest.mock import patch

from bot import SLACK_CLIENT, KARMA_BOT, KARMA_CACHE, MAX_POINTS
from bot import KARMA_ACTION, USERNAME_CACHE, karmas
from bot.slack import post_msg, parse_next_msg, lookup_username, Message
from bot.karma import Karma, _parse_karma_change

userinfo = {
    'user': {
        'name': 'bob',
    }
}

# it's ok to remove the pickle file locally
if os.path.isfile(KARMA_CACHE):
    os.remove(KARMA_CACHE)


class TestKarma(object):
    '''https://realpython.com/blog/python/testing-third-party-apis-with-mocks/'''

    @classmethod
    def setup_class(cls):
        cls.mock_slack_api_call = patch('bot.SLACK_CLIENT.api_call', return_value=userinfo)
        cls.mock_api_call = cls.mock_slack_api_call.start()
        cls.mock_slack_rtm_read = patch('bot.SLACK_CLIENT.rtm_read')
        cls.mock_rtm_read = cls.mock_slack_rtm_read.start()

    @classmethod
    def teardown_class(cls):
        cls.mock_slack_api_call.stop()
        cls.mock_slack_rtm_read.stop()

    def test_lookup_username(self):
        user = lookup_username('@bbelderbos')
        assert user == 'bob'
        assert 'bbelderbos' in USERNAME_CACHE
        assert USERNAME_CACHE.get('bbelderbos') == 'bob'
        assert len(USERNAME_CACHE) == 1
        user = lookup_username('@bbelderbos')
        assert len(USERNAME_CACHE) == 1
        org_name = userinfo['user'].get('name')
        userinfo['user']['name'] = 'tim'
        user = lookup_username('@cook')
        assert user == 'tim'
        assert 'cook' in USERNAME_CACHE
        assert USERNAME_CACHE.get('cook') == 'tim'
        assert len(USERNAME_CACHE) == 2
        user = lookup_username('@cook')
        assert len(USERNAME_CACHE) == 2
        userinfo['user']['name'] = org_name


    def test_parse_next_msg(self):
        self.mock_rtm_read.return_value = None
        assert parse_next_msg() == None
        self.mock_rtm_read.return_value = [
            {'user': 'U5Z6KGX4L'}  # karmabot self
        ]
        assert parse_next_msg() == None
        channel, text = None, 'some text'
        assert parse_next_msg() == None
        channel, text = 'codechallenges', None
        assert parse_next_msg() == None
        channel, text, giverid = 'codechallenges', 'some new message', 'U5Z6ABCDE'
        self.mock_rtm_read.return_value = [
            {'user': giverid,
            'channel': channel,
            'text': text,}
        ]
        assert parse_next_msg() == Message(giverid=giverid, channel=channel, text=text)


    def test_parse_karma_change(self):
        karma_change = '<@bbelderbos>', ' +++'
        receiver, points = _parse_karma_change(karma_change)
        assert receiver == 'bob'
        assert points == 3
        karma_change = 'subject', ' +-++'
        receiver, points = _parse_karma_change(karma_change)
        assert receiver == 'subject'
        assert points == 2
        karma_change = 'subject', ' ++---'
        receiver, points = _parse_karma_change(karma_change)
        assert points == -1


    def test_change_karma(self):
        karma = Karma('bob', 'tim')
        assert karma.change_karma(4) == "tim's karma increased to 4"
        assert karmas.get('tim') == 4
        assert karma.change_karma(2) == "tim's karma increased to 6"
        assert karmas.get('tim') == 6
        assert karma.change_karma(-1) == "tim's karma decreased to 5"
        assert karmas.get('tim') == 5
        msg = "tim's karma increased to 10 (= max increase of {})".format(MAX_POINTS)
        assert karma.change_karma(MAX_POINTS + 3) == msg
        assert karmas.get('tim') == 5 + MAX_POINTS
        msg = "tim's karma decreased to 5 (= max decrease of {})".format(MAX_POINTS)
        prev_score = karmas.get('tim')  # 10
        assert karma.change_karma(-12) == msg
        assert karmas.get('tim') == prev_score - MAX_POINTS  # 5


    def test_change_karma_exceptions(self):
        karma = Karma('bob', 'tim')
        assert_raises(RuntimeError, karma.change_karma, 'string')
        karma = Karma('bob', 'bob')
        assert_raises(ValueError, karma.change_karma, 1)


    def test_change_karma_bot_self(self):
        karma = Karma('bob', 'karmabot')
        assert karma.change_karma(2) == "Thanks @bob for the extra karma, my karma is 2 now"
        karma = Karma('tim', 'karmabot')
        assert karma.change_karma(3) == "Thanks @tim for the extra karma, my karma is 5 now"
        karma = Karma('julian', 'karmabot')
        assert karma.change_karma(-3) == "Not cool @julian lowering my karma to 2, but you are probably right, I will work harder next time"
