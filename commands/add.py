MSG = """Hey {user}, so you want to propose a new command eh?

Awesome! Here are the steps:
1. Karmabot repo: https://github.com/pybites/karmabot
2. Fork the repo, make your branch.
3. Add your command script under the commands/ subdirectory.
4. Open a PR of your branch against PyBites repo.
5. Bob/Julian/Community to approve and merge it in.

Here is a walk-through video:
https://www.youtube.com/watch?v=Yx9qYl6lmzM&t=2s

Thanks!
"""


def add_command(**kwargs):
    """Instructions how to propose a new bot command"""
    user = kwargs.get('user')
    if not user:
        return None
    return MSG.format(user=user)


if __name__ == '__main__':
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = add_command(**kwargs)
    print(output)
