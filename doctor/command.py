# coding=utf-8

"""
Provides a common interface for executing commands.
"""

import sys
import subprocess

from doctor.report import supports_color


def get_argv(cmd: str) -> list:
    """ Return a list of arguments from a full command. """

    return cmd.strip().split(' ')


def display(cmd: str):
    """ Emit a diagnostic message of a command line. """

    stream = sys.stderr

    diagnostic = f'$ {cmd}'
    diagnostic = f'\x1b[0;37m{diagnostic}\x1b[0m' if supports_color(stream) else diagnostic

    print(diagnostic, file=stream)


def execute(cmd: str, show_argv: bool=False, show_output: bool=False) -> int:
    """ Execute a command-line process and return exit code.

    If show_argv is True, display the executed command and its parameters/arguments.
    If show_output is True, display the resulting output from the executed command.

    The resulting output of the executed command is not redirected (unless show_output is False,
    in which case it is quelched), which means it might be printed on either stdout or stderr
    depending on the executed command.
    """

    argv = get_argv(cmd)

    if show_argv:
        display(cmd)

    result = subprocess.run(
        argv,
        stdout=sys.stdout if show_output else subprocess.DEVNULL,
        stderr=sys.stderr if show_output else subprocess.DEVNULL)

    return result.returncode
