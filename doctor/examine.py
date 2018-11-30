# coding=utf-8

"""
Provides functions for examining and diagnosing defects in the current repository.
"""

import subprocess

from doctor import command

from doctor.report import inform, note, conclude


def check_integrity(verbose: bool=False) -> bool:
    """ Return True if repository has internal consistency, False otherwise. """

    if verbose:
        inform('checking internal consistency...')

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


def diagnose(verbose: bool=False):
    if verbose:
        inform('looking for unwanted files...')

    unwanted_files = find_unwanted_files(verbose)

    if len(unwanted_files) > 0:
        for file in unwanted_files:
            note(file)

        conclude('unwanted files are being tracked')
