# coding=utf-8

"""
Provides a common interface for executing commands.
"""

import sys
import subprocess


def execute(cmd: str, message: str=None, verbose: bool=False, output_always: bool=False) -> int:
    """ Execute a command-line process and return exit code.

    If verbose is True, display the provided message (optionally), then display the executed
    command and its resulting output.

    If output_always is True, the resulting output is displayed no matter whether verbose
    is True or not.

    The resulting output of the executed command is not redirected (unless verbose is False,
    in which case it is quelched), which means it might be printed on either stdout or stderr
    depending on the program.
    """

    argv = cmd.strip().split(' ')

    # emit diagnostic output to stderr
    stream = sys.stderr
    # only apply colors if stream is not piped to a file
    use_colors = stream.isatty() and hasattr(stream, 'isatty')

    if verbose:
        msg_diagnostic = message
        cmd_diagnostic = f'$ {cmd}'

        if use_colors:
            msg_diagnostic = '\x1b[1m' + msg_diagnostic + '\x1b[0m'
            cmd_diagnostic = '\x1b[0;37m' + cmd_diagnostic + '\x1b[0m'

        diagnostic = (msg_diagnostic + '\n' +
                      cmd_diagnostic)

        print(diagnostic, file=stream)

    result = subprocess.run(
        argv,
        stdout=sys.stdout if verbose or output_always else subprocess.DEVNULL,
        stderr=sys.stderr if verbose or output_always else subprocess.DEVNULL)

    return result.returncode
