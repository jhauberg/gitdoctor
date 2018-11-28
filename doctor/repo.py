# coding=utf-8

"""
Provides utility functions for repositories.
"""

import os
import subprocess


def is_valid() -> bool:
    """ Return True if current working directory is inside a repository. """

    result = subprocess.run([
        'git', 'rev-parse', '--is-inside-work-tree'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.PIPE,  # capture stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    status = str(result.stdout)

    if 'true' in status.lower():
        return True

    return False

