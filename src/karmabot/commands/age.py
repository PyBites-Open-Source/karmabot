from datetime import datetime

PYBITES_BORN = datetime(year=2016, month=12, day=19)
TODAY = datetime.now()


def pybites_age(**kwargs) -> str:
    """Print PyBites age in days"""
    days_old = (TODAY - PYBITES_BORN).days
    return f"PyBites is {days_old} days old"


if __name__ == "__main__":
    # standalone test
    user, channel, text = "bob", "#general", "some message"
    kwargs = {"user": user, "channel": channel, "text": text}
    output = pybites_age(**kwargs)
    print(output)
