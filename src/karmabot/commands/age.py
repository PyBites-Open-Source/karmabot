from datetime import datetime

PYBITES_BORN = datetime(year=2016, month=12, day=19)


def pybites_age(**kwargs) -> str:
    """Print PyBites age in days"""
    today = datetime.now()
    days_old = (today - PYBITES_BORN).days
    return f"PyBites is {days_old} days old"


if __name__ == "__main__":
    # standalone test
    user, channel, text = "bob", "#general", "some message"
    kwargs = {"user": user, "channel": channel, "text": text}
    output = pybites_age(**kwargs)
    print(output)
