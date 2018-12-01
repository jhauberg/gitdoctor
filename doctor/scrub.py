# coding=utf-8

"""
Provides cleaning functions for the current repository.
"""

from doctor import command

import doctor.repo as repo

GIT_EXPIRE = 'git reflog expire --expire-unreachable=now --all --stale-fix'
GIT_GC = 'git gc --prune=now'
GIT_GC_AGGRESSIVE = GIT_GC + ' --aggressive'
GIT_REPACK = 'git repack -A -d -q --pack-kept-objects'
GIT_PRUNE = 'git prune --verbose'


def trim(aggressively: bool=False, verbose: bool=False) -> int:
    """ Trim the repository and return the difference (in bytes) from before and after.

    The difference is negative if the respository became smaller, positive if it became larger.
    """

    size_before = repo.size_in_bytes()

    command.execute(GIT_EXPIRE, show_argv=verbose, show_output=verbose)

    command.execute(
        (GIT_GC_AGGRESSIVE if aggressively else
         GIT_GC),
        show_argv=verbose, show_output=verbose)

    command.execute(GIT_REPACK, show_argv=verbose, show_output=verbose)
    command.execute(GIT_PRUNE, show_argv=verbose, show_output=verbose)

    size_after = repo.size_in_bytes()
    size_difference = size_before - size_after

    return -size_difference
