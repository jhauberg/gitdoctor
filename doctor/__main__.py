#!/usr/bin/env python
# coding=utf-8

"""
usage: git doctor [--verbose]
       git doctor scrub [--full] [--verbose]

OPTIONS
  -f --full     Run a full scrubdown (might take a while)
  -v --verbose  Show diagnostic messages
  -h --help     Show program help
  --version     Show program version

See https://github.com/jhauberg/gitdoctor for additional details.
"""

import sys
import math

from docopt import docopt

from doctor import exit_if_not_compatible, enable_colors, __version__

from doctor.examine import diagnose, check_integrity
from doctor.scrub import trim

import doctor.repo as repo
import doctor.report as report


def main():
    """ Entry point for invoking the git-doctor cli. """

    exit_if_not_compatible()
    enable_colors()

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
        report.conclude('git executable not found')
        sys.exit(1)

    is_verbose = args['--verbose']

    if not repo.exists():
        report.conclude('must be inside a work tree')
        sys.exit(1)

    has_integrity = check_integrity(verbose=is_verbose)

    if not has_integrity:
        report.conclude('integrity has been corrupted')
        sys.exit(1)

    if args['scrub']:
        size_difference = trim(aggressively=args['--full'], verbose=is_verbose)

        if size_difference != 0:
            shrunk = size_difference < 0

            size_variants = ('B', 'KB', 'MB')
            size_index = int(math.floor(math.log(abs(size_difference), 1024)))
            size = round(abs(size_difference) / math.pow(1024, size_index), 2)

            size_type = size_variants[size_index]

            precision = 2 if size_index > 1 else 0
            result = f'{size:.{precision}f}{size_type}'

            if shrunk:
                report.conclude(f'restored approximately {result} of disk space', positive=True)
    else:
        diagnose(verbose=is_verbose)

    sys.exit(0)


if __name__ == '__main__':
    main()
