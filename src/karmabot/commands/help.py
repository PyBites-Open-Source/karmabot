def create_commands_table(commands):
    """Print this help text"""
    ret = "\n".join(
        [
            "{:<30}: {}".format(name, func.__doc__.strip())
            for name, func in sorted(commands.items())
        ]
    )
    return "```{}```".format(ret)
