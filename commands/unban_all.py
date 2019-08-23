def unban_all(**kwargs: dict) -> str:
    """ban_user will ban a user from giving or taking karma."""
    # kwargs will hold user, channel, text (from a Slack message object)
    # use them like this, or just delete these line:
    user = kwargs.get('user')
    channel = kwargs.get('channel')
    # removing the word ban from the baned user command. 
    with open('BANNED', 'w') as banned_list:
        banned_list.write('')
    msg_text = 'Cleared the ban list'
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
