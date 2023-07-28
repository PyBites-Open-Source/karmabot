"""Nox sessions."""
import os
import tempfile
from typing import Any

import nox
from nox.sessions import Session

package = "karmabot"
locations = "src", "tests", "noxfile.py"
env = {
    "KARMABOT_SLACK_USER": "FAKE_BOT_USER",
    "KARMABOT_GENERAL_CHANNEL": "FAKE_GENERAL_CHANNEL",
    "KARMABOT_LOG_CHANNEL": "FAKE_LOG_CHANNEL",
    "KARMABOT_ADMINS": "FAKE_ADMIN1,FAKE_ADMIN2,FAKE_ADMIN3",
    "KARMABOT_DATABASE_URL": "FAKE_DB_URL",
    "KARMABOT_SLACK_APP_TOKEN": "FAKE_APP_TOKEN",
    "KARMABOT_SLACK_BOT_TOKEN": "FAKE_BOT_TOKEN",
    "KARMABOT_TEST_MODE": "true",
    "SQLALCHEMY_SILENCE_UBER_WARNING": "0",
    "SQLALCHEMY_WARN_20": "1",
}

nox.options.sessions = "tests", "lint", "black", "mypy", "safety"


def install_with_constraints(session: Session, *args: str, **kwargs: Any) -> None:
    """Install packages constrained by Poetry's lock file.

    This function is a wrapper for nox.sessions.Session.install. It
    invokes pip to install packages inside of the session's virtualenv.
    Additionally, pip is passed a constraints file generated from
    Poetry's lock file, to ensure that the packages are pinned to the
    versions specified in poetry.lock. This allows you to manage the
    packages as Poetry development dependencies.

    Arguments:
        session: The Session object.
        args: Command-line arguments for pip.
        kwargs: Additional keyword arguments for Session.install.

    """

    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)

    requirements.close()
    os.unlink(requirements.name)


@nox.session(python=["3.10", "3.11"])
def tests(session: Session) -> None:
    """Run the test suite."""
    args = session.posargs or ["--cov", "-m", "not e2e"]
    session.run("poetry", "install", "--only", "main", external=True)
    install_with_constraints(session, "coverage", "pytest", "pytest-cov", "pytest-mock")
    session.run("pytest", *args, env=env)


@nox.session(python="3.10")
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-bandit",
        "flake8-bugbear",
        "flake8-blind-except",
        "flake8-builtins",
        "flake8-logging-format",
        "flake8-debugger",
        "flake8-use-fstring",
    )
    session.run("flake8", *args)


@nox.session(python="3.10")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    install_with_constraints(session, "black")
    session.run("black", *args)


@nox.session(python="3.10")
def mypy(session: Session) -> None:
    """Type-check using mypy."""
    args = session.posargs or locations
    install_with_constraints(session, "mypy")
    session.run("mypy", *args)


@nox.session(python=["3.10", "3.11"])
def safety(session: Session) -> None:
    """Scan dependencies for insecure packages."""
    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--with",
            "dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        install_with_constraints(session, "safety")
        session.run(
            "safety",
            "check",
            f"--file={requirements.name}",
            "--full-report",
            "--ignore=41002",
        )

    requirements.close()
    os.unlink(requirements.name)


@nox.session(python="3.10")
def coverage(session: Session) -> None:
    """Upload coverage data."""
    install_with_constraints(session, "coverage[toml]")
    session.run("coverage", "report", "--fail-under=40")
    session.run("coverage", "xml", "--fail-under=40")
