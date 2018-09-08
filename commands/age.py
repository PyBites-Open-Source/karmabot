from datetime import datetime

PYBITES_BORN = datetime(year=2016, month=12, day=19)
TODAY = datetime.now()


def pybites_age(**kwargs: dict) -> str:
    """Print PyBites age in days"""
    days_old = (TODAY - PYBITES_BORN).days
    return 'PyBites is {} days old'.format(days_old)


if __name__ == '__main__':
    # standalone test
    user, channel, text = 'bob', '#general', 'some message'
    kwargs = dict(user=user,
                  channel=channel,
                  text=text)
    output = pybites_age(**kwargs)
    print(output)
