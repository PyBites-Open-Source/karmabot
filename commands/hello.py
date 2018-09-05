MSG = """Hey {user}, how are you doing today?
Only answer if you already have coded some Python today ;)"""


def hello_user(**kwargs):
    """A simple hello world message from karmabot"""
    user = kwargs.get('user')
    if not user:
        return None
    return MSG.format(user=user)


if __name__ == '__main__':
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = hello_user(**kwargs)
    print(output)
