# coding=utf-8

"""
Provides cleaning functions for the current repository.
"""

from doctor import command

import doctor.repo as repo


GIT_GC = 'git gc --aggressive --no-prune'  # --auto
GIT_PRUNE = 'git prune --verbose'


def trim(aggressively: bool=False, verbose: bool=False) -> int:
    """ Trim the repository and return the difference (in bytes) from before and after.

    The difference is negative if the respository became smaller, positive if it became larger.
    """

    size_before = repo.size_in_bytes()

    command.execute(GIT_GC, show_argv=verbose, show_output=verbose)


    command.execute(GIT_PRUNE, show_argv=verbose, show_output=verbose)

    size_after = repo.size_in_bytes()
    size_difference = size_before - size_after

    return -size_difference
