# coding=utf-8

"""
Provides utility functions for inspecting the current repository.
"""

import os
import subprocess


def can_be_examined() -> bool:
    """ Return True if git is installed. """

    # assume that if a simple git invocation fails, then git is probably not installed
    # this is a portable way to determine existence of a binary on PATH, versus using
    # platform-specific tools like `which` on macOS or (sometimes) `where` on Windows
    try:
        result = subprocess.run([
            'git', '--version'],
            stdout=subprocess.DEVNULL,  # ignore stdout
            stderr=subprocess.DEVNULL)  # ignore stderr

        return result.returncode == 0
    except OSError:
        return False


def exists() -> bool:
    """ Return True if current working directory is inside the work tree of a repository. """

    result = subprocess.run([
        'git', 'rev-parse', '--is-inside-work-tree'],
        stdout=subprocess.PIPE,  # capture stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    if result.returncode != 0:
        # will exit with non-zero code if not in a git repository at all
        return False

    status = result.stdout.decode('utf-8')

    # certain checks require being inside the work tree; e.g. not inside .git/
    # (for example, finding unwanted files through `git ls-files -i`)
    return 'true' in status.lower()


def default_branch() -> str:
    """ Return the symbolic reference to the default branch. """

    result = subprocess.run([
        'git', 'symbolic-ref', '--short', 'refs/remotes/origin/HEAD'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.PIPE,  # capture stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    name = result.stdout.decode('utf-8')

    return name.strip()


def absolute_path() -> str:
    """ Return the absolute path to the root of current repository. """

    result = subprocess.run([
        'git', 'rev-parse', '--show-toplevel'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.PIPE,  # capture stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    path = result.stdout.decode('utf-8')

    return path.strip()


def size_in_bytes(exclude_work_tree: bool=False) -> int:
    """ Return the size (in bytes) of current repository.

    If exclude_work_tree is True, only count size of the .git directory.
    """

    path = absolute_path()

    if exclude_work_tree:
        path = os.path.join(path, '.git')

    files = (os.path.join(dirpath, filename) for dirpath, dirnames, filenames in os.walk(path) for filename in filenames)
    filesizes = [os.path.getsize(filepath) for filepath in files if not os.path.islink(filepath)]
    size = sum(filesizes)

    return size
