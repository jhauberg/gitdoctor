# coding=utf-8

"""
Provides utility functions for repositories.
"""

import os
import subprocess

from typing import List


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


def has_integrity() -> (bool, List[str]):
    """ Return True if repository has been corrupted, False otherwise. """

    result = subprocess.run([
        'git', 'fsck', '--full', '--strict', '--no-progress'],
        stdout=subprocess.DEVNULL,  # ignore stdout
        stderr=subprocess.PIPE,  # capture stderr
        universal_newlines=True)

    if result.returncode == 0:
        return True, []

    issues = result.stderr.splitlines()

    return False, issues
