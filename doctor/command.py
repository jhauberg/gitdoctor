# coding=utf-8

"""
Provides a common interface for executing commands.
"""

import sys
import subprocess


def execute(cmd: str, message: str=None, verbosely: bool=False):
    """ Execute a command-line process.

    If verbosely is True, display the provided message (optionally), then display the executed
    command and its resulting output.

    The resulting output of the executed command is not redirected (unless verbosely is False,
    in which case it is quelched), which means it might be printed on either stdout or stderr
    depending on the program.
    """

    argv = cmd.strip().split(' ')

    # emit diagnostic output to stderr
    stream = sys.stderr
    # only apply colors if stream is not piped to a file
    use_colors = stream.isatty() and hasattr(stream, 'isatty')

    if verbosely:
        msg_diagnostic = message
        cmd_diagnostic = f'$ {cmd}'

        if use_colors:
            msg_diagnostic = '\x1b[1m' + msg_diagnostic + '\x1b[0m'
            cmd_diagnostic = '\x1b[0;37m' + cmd_diagnostic + '\x1b[0m'

        diagnostic = (msg_diagnostic + '\n' +
                      cmd_diagnostic)

        print(diagnostic, file=stream)

    subprocess.run(
        argv,
        check=True,
        stdout=sys.stdout if verbosely else subprocess.DEVNULL,
        stderr=sys.stderr if verbosely else subprocess.DEVNULL)
