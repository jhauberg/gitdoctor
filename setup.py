#!/usr/bin/env python
# coding=utf-8

"""
Setup script for git-doctor.

https://github.com/jhauberg/gitdoctor

Copyright 2018 Jacob Hauberg Hansen.
License: MIT (see LICENSE)
"""

import sys
import re

from setuptools import setup, find_packages

from doctor import VERSION_PATTERN, exit_if_not_compatible

exit_if_not_compatible()


def determine_version_or_exit() -> str:
    """ Determine version identifier or exit with non-zero status. """

    with open('doctor/__version__.py') as file:
        version_contents = file.read()
        version_match = re.search(VERSION_PATTERN, version_contents, re.M)

        if version_match:
            version = version_match.group(1)

            return version

    sys.exit('Version not found')


VERSION = determine_version_or_exit()

setup(
    name='git-doctor',
    version=VERSION,
    description='Keep a healthy repository',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jhauberg/gitdoctor',
    download_url='https://github.com/jhauberg/gitdoctor/archive/master.zip',
    author='Jacob Hauberg Hansen',
    author_email='jacob.hauberg@gmail.com',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[
        'docopt==0.6.2'
    ],
    entry_points={
        'console_scripts': [
            'git-doctor=doctor.__main__:main',
        ],
    }
)
