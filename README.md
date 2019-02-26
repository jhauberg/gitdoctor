# git-doctor

A [git](https://git-scm.com) [extension](https://www.atlassian.com/git/articles/extending-git) that helps diagnosing your repository for common defects.

## Installation

Install `git-doctor` from source:

```console
$ python setup.py install
```

This will put an executable `git-doctor` binary onto your `PATH`, making `git` able to interact with it.

### Requirements

###### Git versions before 2.17 might not be supported

- Python 3.6+
- [docopt](https://github.com/docopt/docopt)

## Usage

Run `git-doctor` from within a git repository:

```console
$ git doctor
```

This initiates an [examination](#examination) of the git repository found in the current working directory. The program exits with a non-zero status if any program errors (*not defects*) were encountered, zero otherwise.

### Options

```console
usage: git doctor [--verbose]
       git doctor scrub [--verbose] [--aggressive]

OPTIONS
  --aggressive  Run a full scrubdown (might take a while)
  -v --verbose  Show diagnostic messages
  -h --help     Show program help
  --version     Show program version
```

## Examination

The purpose of an examination is to discover and identify defects in a repository.

Assuming the repository is fit and viable for examination, `git-doctor` starts looking for defects and reports any results along the way. This process consists of various standard git commands and checks. **No files are touched during an examination**, and the user must manually take action on any reported defects.

## Scrubdown

**Scrubbing a repository will perform modifications to the files/index.**

A scrubdown performs the basic git housekeeping commands: [`reflog expire`](https://git-scm.com/docs/git-reflog) followed by [`gc`](https://git-scm.com/docs/git-gc) (with `--aggressive` for a full scrubdown), ~~then proceeds to remove any unwanted files and redundant branches~~.

## License

This is a *Free and Open-Source Software project*, released under the [MIT License](LICENSE).
