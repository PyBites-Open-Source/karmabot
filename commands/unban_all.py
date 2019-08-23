def unban_all(**kwargs: dict) -> str:
    """ban_user will ban a user from giving or taking karma."""
    user = kwargs.get('user')
    channel = kwargs.get('channel')
    with open('BANNED', 'w') as banned_list:
        banned_list.write('')
    msg_text = 'Cleared the ban list'
    return msg_text


if __name__ == '__main__':
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = my_command(**kwargs)
    print(output)
