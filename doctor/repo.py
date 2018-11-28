# coding=utf-8

"""
Provides utility functions for inspecting the current repository.
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


def absolute_path() -> str:
    """ Return the absolute path of the repository. """

    result = subprocess.run([
        'git', 'rev-parse', '--show-toplevel'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.PIPE,  # capture stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    path = str(result.stdout)

    return path


def size_in_bytes() -> int:
    """ Return the size (in bytes) of the entire repository. """

    path = absolute_path()

    files = (os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(path) for filename in filenames)
    filesizes = [os.path.getsize(filepath) for filepath in files if not os.path.islink(filepath)]
    size = sum(filesizes)

    return size
