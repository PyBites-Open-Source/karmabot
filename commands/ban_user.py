def ban_user(**kwargs: dict) -> str:
    """ban_user will ban a user from giving or taking karma."""
    # kwargs will hold user, channel, text (from a Slack message object)
    # use them like this, or just delete these line:
    user = kwargs.get('user')
    channel = kwargs.get('channel')
    _payload = kwargs.get('text')
    banned_users = _payload.translate({ord(i): None for i in '<>@'}).strip().split()
    # removing the word ban from the baned user command. 
    banned_users.remove('ban')
    with open('BANNED', 'a') as banned_list:
        for new_user in banned_users:
            banned_list.write('{0}\n'.format(new_user))
    msg_text = 'user(s) {} is/are banned.'.format(banned_users)
    # return a message string
    # msg = ...
    return msg_text


if __name__ == '__main__':
    # standalone test
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = my_command(**kwargs)
    print(output)
