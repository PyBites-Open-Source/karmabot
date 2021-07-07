class GetUserInfoException(Exception):
    """Excpetion if Slack API UserInfo could net retrieved"""

    pass


class CommandNotFoundException(Exception):
    """Exception if a request Command is not found"""

    pass


class CommandExecutionException(Exception):
    """Exception for failures during command execution"""

    pass


class NotInitializedException(Exception):
    """Exception if required values are not initialized properly"""

    pass
