from datetime import datetime

from freezegun import freeze_time

from karmabot.commands.age import pybites_age


@freeze_time(datetime(2017, 8, 23))
def test_pybites_age():
    expected = "PyBites is 247 days old"
    assert pybites_age() == expected
