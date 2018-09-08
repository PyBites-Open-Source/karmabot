"""
0. Save/copy this file to a new file under commands/

1. Add logic to my_command and rename it to something more meaningful.
   Optionally you can access user, channel, text from the passed in **kwargs (don't remove this).

2. Add a useful docstring to your renamed my_command.

3. Return a message string that the command/bot should post to the channel.
   You probably want to add some code under __main__ to make sure the function does what you want ...
   
4. In bot/slack.py import the script, e.g.: from commands.template import my_command

5. Add the command to the appropriate dict: ADMIN_BOT_COMMANDS, PUBLIC_BOT_COMMANDS or PRIVATE_BOT_COMMANDS 
   (public = for us in channels, private = for use in @karmabot DM)

6. PR your work. Thanks
"""

def my_command(**kwargs: dict) -> str:
    """Text that will appear in the help section"""
    # kwargs will hold user, channel, text (from a Slack message object)
    
    # use them like this, or just delete these line:
    user = kwargs.get('user')
    channel = kwargs.get('channel')
    msg_text = kwargs.get('text')
    
    # return a message string
    # msg = ...
    return msg


if __name__ == '__main__':
    # standalone test
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = my_command(**kwargs)
    print(output)
