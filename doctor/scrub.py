# coding=utf-8

"""
Provides cleaning functions for the current repository.
"""

import subprocess

import doctor.repo as repo


def trim():
    size_before = repo.size_in_bytes()

    subprocess.run(['git', 'gc', '--auto', '--aggressive', '--no-prune', '--quiet'], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(['git', 'prune'], check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

    size_after = repo.size_in_bytes()

    size_difference = max(size_before, size_after) - min(size_before, size_after)

    print(f'saved {size_difference} bytes')
