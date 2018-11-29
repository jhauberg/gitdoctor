# coding=utf-8

"""
Provides functions for examining and diagnosing defects in the current repository.
"""

from doctor import command


def check_integrity(verbosely: bool=False) -> bool:
    """ Return True if repository has internal consistency, False otherwise. """

    status = command.execute(
        'git fsck --full --strict' if verbosely else 'git fsck --full --strict --no-progress',
        'Checking internal consistency:', verbosely, output_always=True)

    return status == 0


def diagnose():
    pass
