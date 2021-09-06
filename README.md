# PyBites Karmabot - A Python based Slack Chatbot

[![Tests](https://github.com/PyBites-Open-Source/karmabot/workflows/Tests/badge.svg)](https://github.com/PyBites-Open-Source/karmabot/actions?workflow=Tests) [![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit) [![codecov.io](https://codecov.io/github/PyBites-Open-Source/karmabot/coverage.svg?branch=master)](https://codecov.io/github/PyBites-Open-Source/karmabot?branch=master)

**A Python based Slack Chatbot for Community interaction**

## Features

Karmabot's main features is the management of Karma within the slack community server. You can give karma, reduce karma, check your current karma points and manage your karma related username.

![karma example](https://www.pogross.de/uploads/karmabot.png)

[Demo Youtube Video](https://www.youtube.com/watch?v=Yx9qYl6lmzM&amp;t=2s)

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

However, you need to some setup and supply some settings prior to this.

### Setup

For app creation and tokens please follow the [slack-bolt guide](https://slack.dev/bolt-python/tutorial/getting-started) and enable [socket mode](https://slack.dev/bolt-python/concepts#socket-mode).

#### Settings

By default we will look for a `.karmabot` file in the directory you used the `karmabot` command. The file should supply the following information.

```env
# Slack bot app
KARMABOT_SLACK_BOT_TOKEN=
KARMABOT_SLACK_APP_TOKEN=

# Workspace
KARMABOT_SLACK_USER=
KARMABOT_GENERAL_CHANNEL=
KARMABOT_ADMINS=

# Backend
KARMABOT_DATABASE_URL=

# Testing
KARMABOT_TEST_MODE=
```

KARMABOT_SLACK_BOT_TOKEN
:   The [SLACK_BOT_TOKEN](https://slack.dev/bolt-python/tutorial/getting-started) for your bot. You will find it under **OAuth & Permission 🠊 Bot User OAuth Access Token** in your [app](https://api.slack.com/apps/). The token starts with `xoxb-`.

KARMABOT_SLACK_APP_TOKEN
: The SLACK_APP_TOKEN used for running the bot in [Socket Mode](https://slack.dev/bolt-python/concepts#socket-mode). You will find it under **Basic Information 🠊 App-Level Tokens** in your [app](https://api.slack.com/apps/).
  The token starts with `xapp-`.

KARMABOT_SLACK_USER
: The bot's user id. Initially, you can fill in a placeholder. Once you've run your own Karmabot for the first time, you can ask it as admin in private chat via `@Karmabot your_id`. This will return a value starting with `U`, e.g., `U0123XYZ`. Replace your placeholder with this value.

KARMABOT_GENERAL_CHANNEL
: The channel id of your main channel in slack. Initially, you can fill in a placeholder. Once you've run your own Karmabot for the first time, you can ask it as admin in private chat via `@Karmabot general_channel_id`. This will return a value starting with `C`, e.g., `C0123XYZ`. Replace your placeholder with this value.

KARMABOT_ADMINS
: The [slack user ids](https://api.slack.com/methods/users.identity) of the users that should have admin command access separated by commas.

KARMABOT_DATABASE_URL
  : The database url which should be compatible with SqlAlchemy. For the provided docker file use `postgresql://user42:pw42@localhost:5432/karmabot`.
  :heavy_exclamation_mark: To start the provided Docker-based Postgres server, be sure you have Docker Compose [installed](https://docs.docker.com/compose/install/) and run `docker-compose up -d` from the karmabot directory.

KARMABOT_TEST_MODE=
  : Determines if the code is run in test mode. User `KARMABOT_TEST_MODE=true` to enable testing mode. Everything else will default to `false`. This setting has to be provided as `true`, if you want run tests without a valid `KARMABOT_SLACK_BOT_TOKEN`. Otherwise, you will receive an exceptions with `slack_bolt.error.BoltError: token is invalid ...`.

If you do not want to use a file you have to provide environment variables with the above names. If no file is present we default to environment variables.

#### Permissions

Go to your [slack app](https://api.slack.com/apps/) and click on **Add features and functionality**. Then go into the following categories and set permissions.

- Event Subscriptions
  - Enable Events 🠊 Toggle the slider to on
  - Subscribe to bot events 🠊 Add via the **Add Bot User Event** button
    - team_join
    - channel_create
    - message.channels
    - message.groups
    - message.im
- Permissions
  - Scopes 🠊 Add the following permissions via the **Add an OAuth Scope** button
    - app_mentions:read
    - channels:history
    - channels:join
    - channels:read
    - chat:write
    - groups:history
    - groups:read
    - groups:write
    - im:history
    - im:read
    - im:write
    - users.profile:read
    - users:read

## Development pattern for contributors

We use [poetry](https://github.com/python-poetry/poetry) and `pyproject.toml` for managing packages, dependencies and some settings.

### Setup virtual environment for development

You should follow the [instructions](https://github.com/python-poetry/poetry) to get poetry up and running for your system. We recommend to use a UNIX-based development system (Linux, Mac, WSL). After setting up poetry you can use `poetry install` within the project folder to install all dependencies.

The poetry virtual environment should be available in the the project folder as `.venv` folder as specified in `poetry.toml`. This helps with `.venv` detection in IDEs.

#### Conda users

If you use the Anaconda Python distribution (strongly recommended for Windows users) and `conda create` for your virtual environments, then you will not be able to use the `.venv` environment created by poetry because it is not a conda environment. If you want to use `poetry` disable poetry's behavior of creating a new virtual environment with the following command: `poetry config virtualenvs.create false`. You can add `--local` if you don't want to change this setting globally but only for the current project. See the [poetry configuration docs](https://python-poetry.org/docs/configuration/) for more details.

Now, when you run `poetry install`, poetry will install all dependencies to your conda environment. You can verify this by running `pip freeze` after `poetry install`.

### Testing and linting

For testing you need to install [nox](https://nox.thea.codes/en/stable/) separately from the project venv created by poetry. For testing just use the `nox` command within the project folder. You can run all the nox sessions separately if need, e.g.,

- only linting `nox -rs lint`
- only testing `nox -rs tests`

If `nox` cannot be found, use `python -m nox` instead.

For different sessions see the `nox.py` file. You can run `nox --list` to see a list of all available sessions.

If you want to run tests locally via `pytest` you have to provide a valid `.karmabot` settings file or the respective enviroment variables.

Please make sure all tests and checks pass before opening pull requests!

#### Using nox under Windows and Linux (WSL)

Make sure to delete the `.nox` folder when you switch from Windows to WSL and vice versa, because the environments are not compatible.

### [pre-commit](https://pre-commit.com/)

To ensure consistency you can use pre-commit. `pip install pre-commit` and after cloning the karmabot repo run `pre-commit install` within the project folder.

This will enable pre-commit hooks for checking before every commit.
