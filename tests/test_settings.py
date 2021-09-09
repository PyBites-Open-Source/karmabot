import os
from unittest.mock import patch

import pytest

from karmabot.settings import get_env_var


@pytest.mark.parametrize("env_var", ["true", "false"])
def test_get_env_var(env_var):
    with patch.dict(os.environ, {"KARMABOT_TEST_MODE": env_var}):
        assert get_env_var("KARMABOT_TEST_MODE") == env_var


def test_exception_env_variable_not_found():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError):
            get_env_var("KARMABOT_TEST_MODE")


def test_exception_env_variable_empty():
    with patch.dict(os.environ, {"KARMABOT_TEST_MODE": ""}):
        with pytest.raises(ValueError):
            get_env_var("KARMABOT_TEST_MODE")


def test_return_default_value_if_env_variable_not_set():
    with patch.dict(os.environ, {}, clear=True):
        assert get_env_var("KARMABOT_TEST_MODE", default="false") == "false"
