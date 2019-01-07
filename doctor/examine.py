# coding=utf-8

"""
Provides functions for examining and diagnosing defects in the current repository.
"""

import subprocess

from doctor import command, repo
from doctor.report import note, conclude


def check_integrity(verbose: bool=False) -> (bool, list):
    """ Return True if repository has internal consistency, False otherwise. """

    cmd = 'git fsck --no-progress --strict --full'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE)

    errors = result.stderr.decode('utf-8').splitlines()

    return result.returncode == 0, errors


def find_unreachable_objects(verbose) -> list:
    """ Return a list of unreachable objects eligible for a scrubdown. """

    cmd = 'git fsck --unreachable'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    unreachables = result.stdout.decode('utf-8').splitlines()

    return unreachables


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
    """ Return True if current repository contains a README file, False otherwise.

    Checks for the existence of a file at root-level whose name starts with 'README'.
    """

    # search for existence of any README files, but not recursively
    cmd = 'git ls-files README*'

    if verbose:
        command.display(cmd)

    # set the current working directory as root of the repository to perform search from top-level
    root_path = repo.absolute_path()

    result = subprocess.run(
        command.get_argv(cmd),
        cwd=root_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    files = result.stdout.decode('utf-8').splitlines()

    # the search can potentially result in more than one file, but that is OK
    return len(files) > 0


def find_merged_branches(verbose: bool) -> list:
    """ Return a list of branches (local and remote) that are already merged with master. """

    default_branch_ref = repo.default_branch()
    default_branch_name = default_branch_ref.split('/')[-1]

    cmd = f'git branch -a --merged {default_branch_name}'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    output = result.stdout.decode('utf-8').splitlines()

    # trim each output
    branches = [branch.strip() for branch in output]
    # remove leading asterisk from current branch
    branches = [branch[2:] if branch.startswith('*') else branch for branch in branches]
    # remove default branch references
    branches = [branch for branch in branches
                if not branch.endswith(default_branch_ref) and
                not branch == default_branch_name]

    return branches


def diagnose(verbose: bool=False):
    """ Run all diagnostic checks on current repository. """

    unreachables = find_unreachable_objects(verbose)

    if len(unreachables) > 0:
        for unreachable in unreachables:
            note(unreachable)

        conclude(message='scrubdown is recommended',
                 supplement='Run a scrubdown using `git doctor scrub`.')

    if not contains_readme(verbose):
        conclude(message='missing README',
                 supplement='A README-file should be added to the root of the repository. '
                            'Conventionally, this is the entry point for important information '
                            'related to a project and is expected to contain critical knowledge '
                            'such as instructions on use.')

    redundant_branches = find_merged_branches(verbose)

    if len(redundant_branches) > 0:
        for branch in redundant_branches:
            note(branch)

        conclude(message='redundant branches; already merged with master',
                 supplement='These branches should be deleted (both locally and remote) unless '
                            'they are intentionally long-running and will continue to be used.')

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

        conclude(message='unwanted files are being tracked',
                 supplement='Remove unwanted files from being tracked using '
                            '`git remove --cached <filename>`, or remove them completely (from the '
                            'filesystem) using `git rm <filename>`.')
