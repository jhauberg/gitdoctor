# git-doctor

A [git extension](https://git-scm.com) that helps diagnosing your repository for common defects.

## Installation

Install `git-doctor` from source:

```console
$ python setup.py install
```

This will put an executable `git-doctor` binary onto your `PATH`, making `git` able to interact with it.

### Requirements

- Python 3.6+
- [docopt](https://github.com/docopt/docopt)

## Usage

Run `git-doctor` from within a git repository:

```console
$ git doctor
```

This initiates an [examination](#examination) of the git repository found in the current working directory, if any. The program exits with a non-zero status if any errors (not defects) were encountered, zero otherwise.

### Options

```console
usage: git doctor
       git doctor scrub

OPTIONS
  -h --help    Show program help
  --version    Show program version

See https://github.com/jhauberg/gitdoctor for additional details.
```

## Examination

The purpose of an examination is to discover and identify defects in a repository.

Assuming the repository is fit and viable for examination, `git-doctor` starts looking for defects and reports any results along the way. This process consists of various standard git commands and checks. No files are touched during an examination, and the user must manually take action on any reported defects.

## Scrubdown

**Scrubbing a repository will perform modifications to the files/index.**

A scrubdown performs the basic git housekeeping commands: [`gc`](https://git-scm.com/docs/git-gc) and [`prune`](https://git-scm.com/docs/git-prune), ~~then proceeds to remove any unwanted files and redundant branches~~.

## License

This is a *Free and Open-Source Software project*, released under the [MIT License](LICENSE).
