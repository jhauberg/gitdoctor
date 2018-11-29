# coding=utf-8

"""
Provides cleaning functions for the current repository.
"""

from doctor import command

import doctor.repo as repo


GIT_GC = 'git gc --aggressive --no-prune'  # --auto
GIT_PRUNE = 'git prune --verbose'


def trim(verbosely: bool=False) -> int:
    """ Trim the repository and return the number of bytes saved. """

    size_before = repo.size_in_bytes()

    command.execute(GIT_GC, 'Running garbage collection:', verbosely)
    command.execute(GIT_PRUNE, 'Pruning unreachable objects:', verbosely)

    size_after = repo.size_in_bytes()

    size_difference = max(size_before, size_after) - min(size_before, size_after)

    return size_difference
