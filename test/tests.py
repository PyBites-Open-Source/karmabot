import os
from nose.tools import assert_raises
from unittest.mock import patch

from bot import SLACK_CLIENT, KARMA_BOT, KARMA_CACHE, MAX_POINTS
from bot import KARMA_ACTION, USERNAME_CACHE, karmas
from bot.slack import post_msg, parse_next_msg, lookup_username, Message
from bot.karma import parse_karma_change, change_karma

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
        giver, receiver, points = parse_karma_change('fred', '<@bbelderbos>', ' +++')
        assert giver == 'bob'  # mock lookup_username
        assert receiver == 'bob'
        assert points == 3
        giver, receiver, points = parse_karma_change('fred', 'subject', ' +-++')
        assert receiver == 'subject'
        assert points == 2
        giver, receiver, points = parse_karma_change('fred', 'subject', ' ++---')
        assert points == -1


    def test_change_karma(self):
        assert_raises(ValueError, change_karma, 'bob', 'bob', 4)
        assert_raises(RuntimeError, change_karma, 'bob', 'tim', 'string')
        msg = change_karma('bob', 'tim', 4)
        assert msg == "tim's karma increased to 4"
        assert karmas.get('tim') == 4
        msg = change_karma('bob', 'tim', 2)
        assert karmas.get('tim') == 6
        msg = change_karma('bob', 'tim', -1)
        assert karmas.get('tim') == 5
        assert msg == "tim's karma decreased to 5"
        msg = change_karma('bob', 'tim', MAX_POINTS + 3)
        assert karmas.get('tim') == 5 + MAX_POINTS
        assert msg == "tim's karma increased to 10 (= max increase of {})".format(MAX_POINTS)

