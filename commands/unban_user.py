def unban_user(**kwargs: dict) -> str:
    """ban_user will ban a user from giving or taking karma."""
    # kwargs will hold user, channel, text (from a Slack message object)
    # use them like this, or just delete these line:
    user = kwargs.get('user')
    channel = kwargs.get('channel')
    _payload = kwargs.get('text')
    unbanned_users = _payload.translate({ord(i): None for i in '<>@'}).strip().split()
    # removing the word ban from the baned user command. 
    unbanned_users.remove('unban')
    with open('BANNED', 'r') as banned_list:
        temp_list = banned_list.readlines()
    with open('BANNED', 'w') as banned_list:
        for line in temp_list:
            for user in unbanned_users:
                if line.strip('\n') != user:
                    banned_list.write(line)
    msg_text = 'user(s) {} is/are no longer banned.'.format(unbanned_users)
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
