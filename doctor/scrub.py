# coding=utf-8

"""
Provides cleaning functions for the current repository.
"""

import sys
import subprocess

import doctor.repo as repo


GIT_GC = 'git gc --aggressive --no-prune'  # --auto
GIT_PRUNE = 'git prune --verbose'


def trim(verbosely: bool=False) -> int:
    """ Trim the repository and return the number of bytes saved. """

    size_before = repo.size_in_bytes()

    # todo: this pattern should be refactored into a common function, so that e.g. integrity
    #       checking also shows what it is doing- and any output the action might produce
    #       ideally we would capture output and display it manually in a preferable way (indented?)
    #       or colored, but I think the more pragmatic solution is to just pipe directly to
    #       whatever git feels like; this way we don't have to handle any edge cases
    if verbosely:
        print('\x1b[1mRunning garbage collection:\x1b[0m', file=sys.stderr)
        print(f'\x1b[0;37m$ {GIT_GC}\x1b[0m', file=sys.stderr)

    subprocess.run(
        GIT_GC.split(' '),
        check=True,
        stdout=sys.stdout if verbosely else subprocess.DEVNULL,
        stderr=sys.stderr if verbosely else subprocess.DEVNULL)

    if verbosely:
        print('\x1b[1mPruning unreachable objects:\x1b[0m', file=sys.stderr)
        print(f'\x1b[0;37m$ {GIT_PRUNE}\x1b[0m', file=sys.stderr)

    subprocess.run(
        GIT_PRUNE.split(' '),
        check=True,
        stdout=sys.stdout if verbosely else subprocess.DEVNULL,
        stderr=sys.stderr if verbosely else subprocess.DEVNULL)

    size_after = repo.size_in_bytes()

    size_difference = max(size_before, size_after) - min(size_before, size_after)

    return size_difference
