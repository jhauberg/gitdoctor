# coding=utf-8

"""
Provides functions for examining and diagnosing defects in the current repository.
"""

from doctor import command

from doctor.report import inform


def check_integrity(verbose: bool=False) -> bool:
    """ Return True if repository has internal consistency, False otherwise. """

    if verbose:
        inform('checking internal consistency...')

    status = command.execute(
        ('git fsck --full --strict --unreachable' if verbose else
         'git fsck --full --strict --unreachable --no-progress'),
        show_argv=verbose,
        show_output=True)

    return status == 0


def diagnose():
    pass
