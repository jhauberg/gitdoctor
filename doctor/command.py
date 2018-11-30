# coding=utf-8

"""
Provides a common interface for executing commands.
"""

import sys
import subprocess


def execute(cmd: str, show_argv: bool=False, show_output: bool=False) -> int:
    """ Execute a command-line process and return exit code.

    If show_argv is True, display the executed command and its parameters/arguments.
    If show_output is True, display the resulting output from the executed command.

    The resulting output of the executed command is not redirected (unless show_output is False,
    in which case it is quelched), which means it might be printed on either stdout or stderr
    depending on the executed command.
    """

    argv = cmd.strip().split(' ')

    # emit diagnostic output to stderr
    stream = sys.stderr
    # only apply colors if stream is not piped to a file
    use_colors = stream.isatty() and hasattr(stream, 'isatty')

    if show_argv:
        cmd_diagnostic = (f'\x1b[0;37m$ {cmd}\x1b[0m' if use_colors else
                          f'$ {cmd}')

        print(cmd_diagnostic, file=stream)

    result = subprocess.run(
        argv,
        stdout=sys.stdout if show_output else subprocess.DEVNULL,
        stderr=sys.stderr if show_output else subprocess.DEVNULL)

    return result.returncode
