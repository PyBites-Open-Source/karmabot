import pytest

from karmabot.commands.add import MSG, add_command


@pytest.mark.parametrize(
    "test_id",
    [("ABC123"), ("XYZ789")]
)
def test_add_command(test_id):
    actual = add_command(user_id=test_id)
    expected = MSG.format(username=f"<@{test_id}>")
    assert actual == expected
