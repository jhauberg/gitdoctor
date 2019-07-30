# coding=utf-8

"""
Provides outputting facilities for reports and diagnosis conclusions.
"""

import sys
import textwrap

NEGATIVE = -1
POSITIVE = +1


def supports_color(stream) -> bool:
    """ Determine whether an output stream (e.g. stdout/stderr) supports displaying colored text.

    A stream that is redirected to a file does not support color.
    """

    return stream.isatty() and hasattr(stream, 'isatty')


def important(message: str, *, sentiment: int = NEGATIVE):
    """ Emit an important diagnostic message.

    Important diagnostics go to stdout and are considered as a result output; i.e. output
    that is directly related to the main purpose of the program.

    If supported, color message according to sentiment.

    If a supplementary message is provided, emit it as an informative diagnostic.
    """

    stream = sys.stdout
    output = f'doctor: {message}'

    if supports_color(stream):
        color = ('\x1b[0;34m' if sentiment is POSITIVE else
                 '\x1b[0;91m')

        output = f'{color}{output}\x1b[0m'

    print(output, file=stream)


def information(message: str, *, wrapped: bool = True):
    """ Emit an informative diagnostic message.

    Informative diagnostics go to stderr and must not be a vital resulting output.
    """

    stream = sys.stderr
    output = message

    if wrapped:
        # wrap output so that it does not exceed 70 columns
        output = textwrap.fill(output, width=70)

    print(output, file=stream)


def note(message: str):
    """ Emit a diagnostic message related to an important diagnostic. """

    stream = sys.stdout
    output = message

    if supports_color(stream):
        output = f'\x1b[0;33m{output}\x1b[0m'

    print(output, file=stream)


def conclude(message: str, supplement: str = None, *, sentiment: int = NEGATIVE):
    """ Emit an important diagnostic message as the result of a diagnosis.

    If supported, color message according to sentiment.

    If a supplementary message is provided, emit it as an informative diagnostic.
    """

    important(message, sentiment=sentiment)

    if supplement is not None and len(supplement) > 0:
        information(supplement)
