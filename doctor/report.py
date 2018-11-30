# coding=utf-8

"""
Provides outputting facilities for reports and diagnosis conclusions.
"""

import sys


def supports_color(stream) -> bool:
    """ Determine whether an output stream (e.g. stdout/stderr) supports displaying colored text.

    A stream that is redirected to a file does not support color.
    """
    
    return stream.isatty() and hasattr(stream, 'isatty')


def conclude(message: str, positive: bool=False):
    stream = sys.stdout

    output = f'doctor: {message}'

    if supports_color(stream):
        color = ('\x1b[0;34m' if positive else
                 '\x1b[0;91m')

        output = f'{color}{output}\x1b[0m'

    print(output, file=stream)


def inform(message: str):
    stream = sys.stderr

    print(f'doctor: {message}', file=stream)
