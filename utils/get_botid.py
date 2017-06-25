import sys

from bot import SLACK_CLIENT

BOT_NAME = 'karmabot'

api_call = SLACK_CLIENT.api_call("users.list")

if not api_call.get('ok'):
    err = api_call.get('error', 'none')
    print('could not get users.list, error: {}'.format(err))
    sys.exit(1)

users = api_call.get('members')
for user in users:
    if 'name' in user and user.get('name') == BOT_NAME:
        print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
