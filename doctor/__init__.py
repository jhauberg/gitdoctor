# coding=utf-8

import sys

VERSION_PATTERN = r'^__version__ = [\'"]([^\'"]*)[\'"]'


def is_compatible() -> bool:
    """ Determine whether the Python version is supported. """

    if sys.version_info < (3, 6):
        return False

    return True


def exit_if_not_compatible():
    """ Exit with non-zero status if system is running unsupported Python version. """

    if not is_compatible():
        sys.exit('Python 3.6+ required')
