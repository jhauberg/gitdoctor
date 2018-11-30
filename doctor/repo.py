# coding=utf-8

"""
Provides utility functions for inspecting the current repository.
"""

import os
import subprocess


def can_be_examined() -> bool:
    """ Return True if git is installed. """

    result = subprocess.run([
        'git', '--version'],
        stdout=subprocess.DEVNULL,  # ignore stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    if result.returncode == 0:
        return True

    return False


def exists() -> bool:
    """ Return True if current working directory is inside a repository. """

    result = subprocess.run([
        'git', 'rev-parse', '--is-inside-work-tree'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.PIPE,  # capture stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    status = result.stdout.decode('utf-8')

    if 'true' in status.lower():
        return True

    return False


def absolute_path() -> str:
    """ Return the absolute path of the repository. """

    result = subprocess.run([
        'git', 'rev-parse', '--show-toplevel'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.PIPE,  # capture stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    path = result.stdout.decode('utf-8')

    return path


def size_in_bytes() -> int:
    """ Return the size (in bytes) of the entire repository. """

    path = absolute_path()

    files = (os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(path) for filename in filenames)
    filesizes = [os.path.getsize(filepath) for filepath in files if not os.path.islink(filepath)]
    size = sum(filesizes)

    return size
