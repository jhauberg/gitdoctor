#!/usr/bin/env python
# coding=utf-8

"""
usage: git doctor
       git doctor scrub

OPTIONS
  -h --help    Show program help
  --version    Show program version

See https://github.com/jhauberg/gitdoctor for additional details.
"""

import sys

from docopt import docopt

from doctor import exit_if_not_compatible, __version__

from doctor.examine import diagnose
from doctor.scrub import trim

import doctor.repo as repo


def main():
    """ Entry point for invoking the git-doctor cli. """

    exit_if_not_compatible()

    argv = sys.argv

    # insert 'doctor' as first argument, otherwise docopt won't match the usage pattern
    # (docopt doesn't care about matching name of calling program, so inserting this argument will
    # work in both cases, whether using git redirection or calling the 'git-doctor' binary directly-
    # the usage example could specify 'asdasd' as calling program and it would still work out-
    # alternatively, replacing 'git doctor' with 'git-doctor' in the usage example would remove
    # the need for inserting this argument, but it would look bad!)
    argv[0] = 'doctor'

    args = docopt(__doc__, argv=argv, version='git-doctor ' + __version__.__version__)

    is_in_repository = repo.is_valid()

    if not is_in_repository:
        sys.exit('Not a git repository')

    has_integrity, issues = repo.has_integrity()

    if not has_integrity:
        errors = '\n'.join(['  ' + line for line in issues])
        message = (f'Repository has integrity issues:\n'
                   f'{errors}')

        sys.exit(message)

    if args['scrub']:
        bytes_saved = trim()

        print(f'saved {bytes_saved} bytes', file=sys.stderr)
    else:
        diagnose()

    sys.exit(0)


if __name__ == '__main__':
    main()
