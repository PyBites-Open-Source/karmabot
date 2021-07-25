from datetime import datetime

PYBITES_BORN = datetime(year=2016, month=12, day=19)


def pybites_age(**kwargs) -> str:
    """Print PyBites age in days"""
    today = datetime.now()
    days_old = (today - PYBITES_BORN).days
    return f"PyBites is {days_old} days old"
