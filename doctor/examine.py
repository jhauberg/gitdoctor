# coding=utf-8

"""
Provides functions for examining and discovering defects in the current repository.
"""

import subprocess

from doctor import command, repo


def check_eligibility(verbose: bool=False) -> (bool, list):
    """ Return True if repository is eligible for examination, False otherwise.

    Determine eligibility by whether or not a `git fsck` check passes and produces no issues.
    """

    cmd = 'git fsck --no-progress --strict --full'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE)

    issues = result.stderr.decode('utf-8').splitlines()

    is_eligible = result.returncode == 0 and len(issues) == 0

    return is_eligible, issues


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

    # to avoid exceeding max argument/commandline length, we split input into chunks if necessary
    # the chunk size is completely arbitrary, but larger is better (fewer git executions)
    chunk_size = 1024

    if len(filepaths) > chunk_size:
        chunks = [filepaths[i:i + chunk_size] for i in range(0, len(filepaths), chunk_size)]

        sources = []

        for chunk in chunks:
            sources.extend(get_exclusion_sources(chunk, verbose))
            # disable verbosity after first execution
            verbose = False

        return sources

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


def find_merged_branches(remote: str, verbose: bool) -> (list, str):
    """ Return a list of branches that are merged with default branch on a remote. """

    default_branch = repo.default_branch(remote)

    cmd = f'git branch --all --merged {default_branch}'

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
                if not branch.endswith(default_branch) and
                not branch == default_branch]

    return branches, default_branch
