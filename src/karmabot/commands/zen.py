import contextlib
import io


def import_this(**kwargs):
    """Print the Zen of Python"""
    # https://stackoverflow.com/a/23794519
    zen = io.StringIO()
    with contextlib.redirect_stdout(zen):
        import this  # noqa: F401

    text = f"```{zen.getvalue()}```"
    return text
