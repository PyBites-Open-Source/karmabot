from bot import karmas

MSG = """Hey {user}, your current karma is {score}"""
TOP_NUMBER = 10


def get_karma(**kwargs):
    """Lookup your current karma score"""
    user = kwargs.get('user')
    if not user:
        return 'User not found'

    score = karmas.get(user)
    if score is None:
        return 'No karma score for user'

    return MSG.format(user=user, score=score)


def top_karma(**kwargs):
    """Get the PyBites members with most karma"""
    output = ['PyBites members with most karma:']
    for person, score in karmas.most_common(TOP_NUMBER):
        output.append('{:<20} -> {}'.format(person, score))
    return '\n'.join(output)


if __name__ == '__main__':
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = get_karma(**kwargs)

    output = top_karma(**kwargs)
    print(output)
