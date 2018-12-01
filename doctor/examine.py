# coding=utf-8

"""
Provides functions for examining and diagnosing defects in the current repository.
"""

import subprocess

from doctor import command



def check_integrity(verbose: bool=False) -> bool:
    """ Return True if repository has internal consistency, False otherwise. """

    status = command.execute(
        ('git fsck --full --strict --unreachable' if verbose else
         'git fsck --full --strict --unreachable --no-progress'),
        show_argv=verbose,
        show_output=True)

    return status == 0


def find_unwanted_files(verbose: bool=False) -> list:
    cmd = 'git ls-files -i --exclude-standard'

    if verbose:
        command.display(cmd)

    result = subprocess.run(
        command.get_argv(cmd),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    files = result.stdout.decode('utf-8').splitlines()

    return files


def get_exclusion_sources(filepaths: list, verbose: bool) -> list:
    cmd = 'git check-ignore --no-index --verbose ...'

    if verbose:
        command.display(cmd)

    cmd = cmd.replace('...', ' '.join(filepaths))

    result = subprocess.run(
        command.get_argv(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL)

    sources = result.stdout.decode('utf-8').splitlines()

    if len(sources) > 0:
        # the format is <source>:<linenum>:<pattern>\t<pathname>
        sources = [':'.join(source.split(':')[:2]) for source in sources]

    return sources


def diagnose(verbose: bool=False):
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
