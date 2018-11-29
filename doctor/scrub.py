# coding=utf-8

"""
Provides cleaning functions for the current repository.
"""

import subprocess

import doctor.repo as repo


def trim() -> int:
    """ Trim the repository and return the number of bytes saved. """

    size_before = repo.size_in_bytes()

    subprocess.run([
        'git', 'gc', '--auto', '--aggressive', '--no-prune', '--quiet'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.DEVNULL,  # ignore stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    subprocess.run([
        'git', 'prune'],
        check=True,  # print stacktrace on non-zero exit status
        stdout=subprocess.DEVNULL,  # ignore stdout
        stderr=subprocess.DEVNULL)  # ignore stderr

    size_after = repo.size_in_bytes()

    size_difference = max(size_before, size_after) - min(size_before, size_after)

    return size_difference
