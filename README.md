# PyBites Karmabot - A Python based Slack Chatbot

[![Tests](https://github.com/pogross/karmabot/workflows/Tests/badge.svg)](https://github.com/pogross/karmabot/actions?workflow=Tests) [![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) [![BCH compliance](https://bettercodehub.com/edge/badge/pybites/karmabot?branch=master)](https://bettercodehub.com/) [![codecov](https://codecov.io/gh/pogross/karmabot/branch/hypermodern-karmabot/graph/badge.svg)](https://codecov.io/gh/pogross/karmabot)

**A Python based Slack Chatbot for Community interaction**

## Features

Karmabot's main features is the management of Karma within the slack community server. You can give karma, reduce karma, check your current karma points and manage your karma related username.

![karma example](https://www.pogross.de/uploads/karmabot.png)

https://www.youtube.com/watch?v=Yx9qYl6lmzM&amp;t=2s

Additional commands / features are:

- Jokes powered by [PyJokes](https://github.com/pyjokes/pyjokes)
- Overview on top channels of the slack server
- Random Python tip, quote or nugget from CodeChalleng.es
- Browse and search python documentation, "pydoc help"

## Installation

`pip install karmabot`

## Basic Usage

After installing you can start karmabot by using the command

```bash
karmabot
```

However, you need to supply some settings prior to this.

### Settings

By default we will look for a `.karmabot` file in the directory you used the `karmabot` command. The file should supply the following information.

```env
KARMABOT_SLACK_USER=
KARMABOT_SLACK_TOKEN=
KARMABOT_SLACK_INVITE_USER_TOKEN=
KARMABOT_DATABASE_URL=
KARMABOT_GENERAL_CHANNEL=
KARMABOT_ADMINS=
```

- KARMABOT_SLACK_USER
  The [bot's slack user id](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace).

- KARMABOT_SLACK_TOKEN
  The [auth toke](https://slack.com/help/articles/115005265703-Create-a-bot-for-your-workspace) for your bot

- KARMABOT_SLACK_INVITE_USER_TOKEN
  An invite token to invite the bot to new channels. Bots cannot autojoin channels, but we implemented an invite procedure for this.

- KARMABOT_DATABASE_URL
  The database url which should be compatible with SqlAlchemy. For the provided docker file use postgres://user42:pw42@localhost:5432/karmabot

- KARMABOT_GENERAL_CHANNEL
  The channel id of your main channel slack

- KARMABOT_ADMINS
  The [slack user ids](https://api.slack.com/methods/users.identity) of the users that should have admin command access separated by commas.

If you do not want to use a file you have to provide environment variables with the above names. If no file is present we default to environment variables.

## Development pattern for contributors

We use [poetry](https://github.com/python-poetry/poetry) and `pyproject.toml` for managing packages, dependencies and some settings.

### Setup virtual environment for development

You should follow the [instructions](https://github.com/python-poetry/poetry) to get poetry up and running for your system. We recommend to use a UNIX-based development system (Linux, Mac, WSL). After setting up poetry you can use `poetry install` within the project folder to install all dependencies.

The poetry virtual environment should be available in the the project folder as `.venv` folder as specified in `poetry.toml`. This helps with `.venv` detection in IDEs.

### Testing and linting

For testing you need to install [nox](https://nox.thea.codes/en/stable/) separately from the project venv created by poetry. For testing just use the `nox` command within the project folder. You can run all the nox sessions separately if need, e.g.,

- only linting `nox -rs lint`
- only testing `nox -rs test`

For different sessions see the `nox.py` file. Please make sure all tests and checks pass before opening pull requests!

### [pre-commit](https://pre-commit.com/)

To ensure consistency you can use pre-commit. `pip install pre-commit` and after cloning the karmabot repo run `pre-commit install` within the project folder.

This will enable pre-commit hooks for checking before every commit.
