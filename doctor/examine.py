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
    """ Return a list of tracked files that match a gitignore-rule.

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


def find_excluded_files(verbose: bool=False) -> list:
    """ Return a list of both tracked and untracked files that match a gitignore-rule. """

    cmd = 'git ls-files --others --ignored --exclude-standard'

    if verbose:
        command.display(cmd)

    root_path = repo.absolute_path()

    result = subprocess.run(
        command.get_argv(cmd),
        cwd=root_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    files = result.stdout.decode('utf-8').splitlines()

    return files


def is_file_tracked(filepath: str, verbose: bool=False) -> bool:
    """ Return True if file is tracked in current repository, False otherwise. """

    cmd = f'git ls-files --error-unmatch {filepath}'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)

    return result.returncode == 0


def find_local_tags(verbose: bool=False) -> list:
    """ Return a list of local tags. """

    cmd = 'git tag --list'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    tags = result.stdout.decode('utf-8').splitlines()

    return tags


def find_remote_tags(verbose: bool=False) -> list:
    """ Return a list of remote tags. """

    cmd = 'git ls-remote --tags --quiet'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    tags = result.stdout.decode('utf-8').splitlines()

    # assume format like '<commit>    refs/tags/<tag>'
    tags = [tag.split('/')[-1] for tag in tags]

    return tags


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
    formatted_sources = [':'.join(source.split(':')[:2]) for source in sources]

    return formatted_sources


def contains_readme(verbose: bool=False) -> bool:
    """ Return True if current repository tracks a README file at root level, False otherwise.

    Note that this check only applies to files tracked by the index; return True only if a README-
    file exists on the filesystem and is also under version control.
    """

    # search for existence of any README files, but not recursively
    # (in tracked files; add --others to search untracked)
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

    cmd = f'git branch --all --merged {default_branch_name}'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        check=True,
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
                 supplement='As per convention, a README-file should exist and be tracked at the '
                            'root of repository.')

    local_tags = find_local_tags(verbose)
    remote_tags = find_remote_tags(verbose)

    missing_tags = [tag for tag in local_tags if tag not in remote_tags]

    if len(missing_tags) > 0:
        for tag in missing_tags:
            note(tag)

        conclude(message='local tags not present on remote',
                 supplement='These tags should either be deleted using `git tag -d <tag>`, or '
                            'synced to remote using `git push --tags`. Alternatively, to easily '
                            'match remote, use `git tag -d $(git tag)` (deleting all local tags), '
                            'followed by `git fetch --tags` (fetching all remote tags).')

    redundant_branches = find_merged_branches(verbose)

    if len(redundant_branches) > 0:
        for branch in redundant_branches:
            note(branch)

        conclude(message='redundant branches; already merged with master',
                 supplement='These branches should be deleted (both locally and remote) unless '
                            'they will continue to be used and are intentionally long-running.')

    unwanted_files = find_unwanted_files(verbose)

    if len(unwanted_files) > 0:
        sources = []

        if verbose:
            sources = get_exclusion_sources(unwanted_files, verbose)

            assert len(sources) == len(unwanted_files)

        for i, file in enumerate(unwanted_files):
            if verbose:
                source = sources[i]
                file = f'{file} ({source})'

            note(file)

        conclude(message='unwanted files are being tracked',
                 supplement='Remove unwanted files from being tracked using '
                            '`git remove --cached <filename>`, or remove them completely (from the '
                            'filesystem) using `git rm <filename>`.')
