import contextlib
import io


def import_this(**kwargs):
    """Print the Zen of Python"""
    # https://stackoverflow.com/a/23794519
    zen = io.StringIO()
    with contextlib.redirect_stdout(zen):
        import this  # noqa: F401

    return zen.getvalue()


if __name__ == "__main__":
    user, channel, text = "bob", "#general", "some message"
    kwargs = dict(user=user, channel=channel, text=text)
    output = import_this(**kwargs)
    print(output)
