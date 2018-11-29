#!/usr/bin/env python
# coding=utf-8

"""
usage: git doctor [--verbose]
       git doctor scrub [--verbose]

OPTIONS
  -v --verbose  Show diagnostic messages
  -h --help     Show program help
  --version     Show program version

See https://github.com/jhauberg/gitdoctor for additional details.
"""

import sys

from docopt import docopt

from doctor import exit_if_not_compatible, __version__

from doctor.examine import diagnose, check_integrity
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

    if not repo.can_be_examined():
        sys.exit('git executable not found')

    is_verbose = args['--verbose']

    if not repo.exists():
        sys.exit('Not a git repository')

    has_integrity = check_integrity(verbose=is_verbose)

    if not has_integrity:
        sys.exit('Repository has integrity issues')

    if args['scrub']:
        bytes_saved = trim(verbose=is_verbose)

        print(f'Saved {bytes_saved} bytes.')
    else:
        diagnose()

    sys.exit(0)


if __name__ == '__main__':
    main()
