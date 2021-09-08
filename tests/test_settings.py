import os
from unittest.mock import patch

import pytest

from karmabot.settings import _get_env_var


@pytest.mark.parametrize("env_var", ["true", "false"])
def test_get_env_var(env_var):
    with patch.dict(os.environ, {"KARMABOT_TEST_MODE": env_var}):
        assert _get_env_var("KARMABOT_TEST_MODE") == env_var


def test_exception_env_variable_not_found():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError):
            _get_env_var("KARMABOT_TEST_MODE")


def test_exception_env_variable_empty():
    with patch.dict(os.environ, {"KARMABOT_TEST_MODE": ""}):
        with pytest.raises(ValueError):
            _get_env_var("KARMABOT_TEST_MODE")


def test_return_default_value_if_env_variable_not_set():
    with patch.dict(os.environ, {}, clear=True):
        assert _get_env_var("KARMABOT_TEST_MODE", default="false") == "false"
