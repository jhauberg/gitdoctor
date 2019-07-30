# coding=utf-8

"""
Provides functions for diagnosing defects in the current repository.
"""

from doctor.report import note, conclude
from doctor.examine import *

from typing import List


def examine_scrubdown(*, verbose: bool = False):
    """ Examine and diagnose whether current repository could use a scrubdown. """

    unreachables = find_unreachable_objects(verbose)

    if len(unreachables) == 0:
        return

    for unreachable in unreachables:
        note(unreachable)

    conclude(message='scrubdown is recommended',
             supplement='Run a scrubdown using `git doctor scrub`.')


def examine_readme(*, verbose: bool = False):
    """ Examine and diagnose whether current repository contains a README. """

    if contains_readme(verbose):
        return

    conclude(message='README not found',
             supplement='As per convention, a README-file should exist and be tracked at the '
                        'root of the repository.')


def examine_unwanted_files(*, verbose: bool = False):
    """ Examine and diagnose whether current repository tracks unwanted files. """

    unwanted_files = find_unwanted_files(verbose)

    if len(unwanted_files) == 0:
        return

    sources: List[str] = []

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


def examine_excluded_files(*, verbose: bool = False):
    """ Examine and diagnose whether current repository has untracked .gitignore rules. """

    excluded_files = find_excluded_files(verbose)

    if len(excluded_files) == 0:
        return

    sources = get_exclusion_sources(excluded_files, verbose)

    assert len(sources) == len(excluded_files)

    source_filepaths = [source.split(':')[0] for source in sources]

    tracked_source_filepaths = [source for source in set(source_filepaths)
                                if is_file_tracked(source, verbose)]

    has_untracked_rules = False

    for i, file in enumerate(excluded_files):
        source = sources[i]
        source_filepath = source_filepaths[i]

        if source_filepath in tracked_source_filepaths:
            # skip this exclusion
            continue

        has_untracked_rules = True

        file = f'{file} ({source})'

        note(file)

    if not has_untracked_rules:
        return

    conclude(message='files are being excluded by untracked rules',
             supplement='Consider whether any of these files should also be excluded by '
                        'other contributors; if so, adding any applicable rules to a '
                        'tracked .gitignore file would be preferable.')


def examine_missing_tags(*, verbose: bool = False):
    """ Examine and diagnose whether current repository has unpublished tags.

    This examination assumes that current repository has a remote.
    """

    local_tags = find_local_tags(verbose)
    remote_tags = find_remote_tags(verbose)

    missing_tags = [tag for tag in local_tags
                    if tag not in remote_tags]

    if len(missing_tags) == 0:
        return

    for tag in missing_tags:
        note(tag)

    conclude(message='local tags not present on remote',
             supplement='These tags should either be deleted using `git tag -d <tag>`, or '
                        'synced to remote using `git push --tags`. Alternatively, to '
                        'easily match remote, use `git tag -d $(git tag)` (deleting all '
                        'local tags), followed by `git fetch --tags` (fetching all remote '
                        'tags).')


def examine_redundant_branches(remote: str, *, verbose: bool = False):
    """ Examine and diagnose whether current repository has redundant branches.

    This examination assumes that current repository has a remote.
    """

    redundant_branches, default_branch = find_merged_branches(remote, verbose)

    if len(redundant_branches) == 0:
        return

    for branch in redundant_branches:
        note(branch)

    conclude(message=f'redundant branches; already merged with \'{default_branch}\'',
             supplement='These branches should be deleted (both locally and remote) unless '
                        'they will continue to be used and are intentionally long-running.')


def diagnose(*, verbose: bool = False):
    """ Run all examinations on current repository. """

    examine_scrubdown(verbose=verbose)
    examine_readme(verbose=verbose)

    default_remote = repo.default_remote()

    if default_remote is not None:
        examine_missing_tags(verbose=verbose)
        examine_redundant_branches(default_remote, verbose=verbose)

    examine_excluded_files(verbose=verbose)
    examine_unwanted_files(verbose=verbose)
