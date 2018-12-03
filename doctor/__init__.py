# coding=utf-8

import os
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


def is_windows_environment() -> bool:
    """ Return True if on a Windows platform, False otherwise. """

    return os.name == 'nt'


def enable_colors():
    """ Enable terminal color support.

    Only has an effect on Windows.
    """

    if is_windows_environment():
        # enable color escape processing on Windows
        # see https://stackoverflow.com/a/36760881/144433
        import ctypes

        kernel32 = ctypes.windll.kernel32

        STD_OUTPUT_HANDLE = -11

        handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        ENABLE_PROCESSED_OUTPUT = 0x0001
        ENABLE_WRAP_AT_EOL_OUTPUT = 0x0002
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004

        mode = (ENABLE_PROCESSED_OUTPUT |
                ENABLE_WRAP_AT_EOL_OUTPUT |
                ENABLE_VIRTUAL_TERMINAL_PROCESSING)

        kernel32.SetConsoleMode(handle, mode)
