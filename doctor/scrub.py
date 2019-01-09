# coding=utf-8

"""
Provides cleaning functions for the current repository.
"""

from doctor import command

import doctor.repo as repo

GIT_EXPIRE = 'git reflog expire --expire-unreachable=now --all --stale-fix'
GIT_GC = 'git gc --prune=now'
GIT_GC_AGGRESSIVE = GIT_GC + ' --aggressive'


def trim(aggressively: bool=False, verbose: bool=False) -> int:
    """ Trim current repository and return the difference (in bytes) from before and after.

    The difference is negative if the repository became smaller, positive if it became larger.
    """

    # only check size of the .git directory
    only_count_git_dir = True

    size_before = repo.size_in_bytes(exclude_work_tree=only_count_git_dir)

    # expire all reflog entries to unreachable objects immediately, enabling pruning through gc
    command.execute(GIT_EXPIRE, show_argv=verbose, show_output=verbose)

    # run garbage collection; automatically triggers prune, repack and more
    command.execute(
        (GIT_GC_AGGRESSIVE if aggressively else
         GIT_GC),
        show_argv=verbose,
        show_output=verbose)

    size_after = repo.size_in_bytes(exclude_work_tree=only_count_git_dir)
    size_difference = size_before - size_after

    return -size_difference
