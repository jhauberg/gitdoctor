# coding=utf-8

"""
Provides functions for examining and diagnosing defects in the current repository.
"""

import subprocess

from doctor import command, repo
from doctor.report import note, conclude

GIT_FSCK = 'git fsck --unreachable --strict --full'
GIT_FSCK_QUIET = GIT_FSCK + ' --no-progress'


def check_integrity(verbose: bool=False) -> bool:
    """ Return True if repository has internal consistency, False otherwise. """

    status = command.execute(
        (GIT_FSCK if verbose else
         GIT_FSCK_QUIET),
        show_argv=verbose,
        show_output=True)

    return status == 0


def find_unwanted_files(verbose: bool=False) -> list:
    """ Return a list of files that are being tracked but also match a gitignore-rule.

    Check against any viable gitignore location; e.g. any of the following:
        .git/info/exclude
        .gitignore in each directory (at or below current working directory)
        user’s global exclusion file
    """

    cmd = 'git ls-files --ignored --exclude-standard'

    if verbose:
        command.display(cmd)

    # we need to set the current working directory as the root of the repository
    # otherwise we might miss .gitignore files located in directories above
    root_path = repo.absolute_path()

    result = subprocess.run(
        command.get_argv(cmd),
        cwd=root_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    files = result.stdout.decode('utf-8').splitlines()

    return files


def get_exclusion_sources(filepaths: list, verbose: bool) -> list:
    """ Determine which gitignore-rule and file is the source of a file being excluded.

    Return a list that is synchronous and identical in length to the provided filepaths.
    """

    cmd = 'git check-ignore --no-index --verbose ...'

    if verbose:
        command.display(cmd)

    cmd = cmd.replace('...', ' '.join(filepaths))

    result = subprocess.run(
        command.get_argv(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    sources = result.stdout.decode('utf-8').splitlines()

    assert len(sources) == len(filepaths)

    # the format is <source>:<linenum>:<pattern>\t<pathname>
    # resulting format is <source>:<linenum>
    return[':'.join(source.split(':')[:2]) for source in sources]


def contains_readme(verbose: bool=False) -> bool:
    """ Return True if current repository contains README.md at root-level, False otherwise. """

    cmd = 'git ls-files README.md'

    if verbose:
        command.display(cmd)

    # set the current working directory as root of the repository to limit results to this directory
    # as the command does not recurse through subdirectories, we should get exactly 1 line of output
    # if a README.md exists at the root level, 0 otherwise
    root_path = repo.absolute_path()

    result = subprocess.run(
        command.get_argv(cmd),
        cwd=root_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    files = result.stdout.decode('utf-8').splitlines()

    return len(files) == 1


def diagnose(verbose: bool=False):
    """ Run all diagnostic checks on current repository. """

    if not contains_readme(verbose):
        conclude('missing README.md')

    unwanted_files = find_unwanted_files(verbose)

    if len(unwanted_files) > 0:
        sources = []

        if verbose:
            sources = get_exclusion_sources(unwanted_files, verbose)

        for i, file in enumerate(unwanted_files):
            if verbose and len(sources) > 0:
                source = sources[i]
                file = f'{file} ({source})'

            note(file)

        conclude('unwanted files are being tracked')
