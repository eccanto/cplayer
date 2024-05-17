# CPlayer

![](https://img.shields.io/badge/-Linux-grey?logo=linux)
![](https://img.shields.io/pypi/v/cplayer)
![](https://img.shields.io/badge/license-MIT-green)
![](https://img.shields.io/github/stars/eccanto)

![CPlayer](https://raw.githubusercontent.com/eccanto/cplayer/main/documentation/videos/cplayer.gif)

**C**ommand Line **P**ython p**layer** is a minimalist song player written with Python
([github](https://github.com/eccanto/cplayer)), this application offers a wide range of functionality to
enhance your music listening, playlist management, filtering and searching songs and more using keyboard shortcuts.

Below, you'll find a comprehensive list of keyboard shortcuts and their corresponding actions within the application,
and additional configurations: [keyboard shortcuts and customized configurations](cplayer/documentation/help.md).

Only tested in Linux.

## Table of contents

* [Features](#features)
* [Get started](#get-started)
  * [Installation](#installation)
  * [Uninstallation](#uninstallation)
  * [Usage](#usage)
  * [Options](#options)
* [TODO](#todo)
* [Known issues](#known-issues)
* [Reports and Debugging](#reports-and-debugging)
* [Developers](#developers)
  * [Dependencies](#dependencies)
  * [Set up pre-commit](#set-up-pre-commit)
  * [Basic configuration](#basic-configuration)
  * [Testing](#testing)
  * [Advanced configuration](#advanced-configuration)
  * [Static code analysis tools](#static-code-analysis-tools)
    * [Python static checkers](#python-static-checkers)
    * [Run manually](#run-manually)
* [License](#license)
* [Changelog](#changelog)

## Features

* GUI customization.
    * If your system does not support the icons used you can set them manually in [~/.config/cplayer/config.yaml](cplayer/resources/config/default.yaml).
* Keyboard shortcuts customization.
* Create multiple playlists and manage then.
* Multiple ways to navigate through the playlist including jumping by position, filtering, manual displacements,
  sorting, etc.
* Download song from a YouTube URL (`--url`).

## Get started

### Installation

This application can be simply installed by running:

```bash
pip install cplayer
```

if you want to install from a source distribution:

```bash
git clone https://github.com/eccanto/cplayer
cd cplayer/
pip install .
```

### Uninstallation

To uninstall the application you can use `pip`:

```bash
pip uninstall cplayer
```

### Usage

To run the application you must run the command line:

```bash
cplayer
```

By default the application will load the last playlist if it exists, otherwise the application will use the current
path to load the `.mp3` and `.wav` files from the directory (not recursively).

### Options

```
$ cplayer --help

Usage: cplayer [OPTIONS]

  Command Line Python player CLI.

  This command line tool plays music files from a specified directory or last
  used playlist.

  Examples:

      - Play music from the current directory or the last used playlist if it
      exists:

        $ cplayer

      - Play music from a specific directory:

        $ cplayer --path /path/to/music_directory

      - Download song from YouTube

        $ cplayer --url 'https://www.youtube.com/watch?v=xyz'

  For more information, visit https://github.com/eccanto/cplayer

Options:
  -p, --path PATH  Path to the directory containing your music files.
  -u, --url TEXT   URL of the song to download from YouTube.
  --version        Show the version and exit.
  --help           Show this message and exit.
```

### TODO

* Add favorites feature.
* Add option to restore default configurations.
* Add confirmation dialog to remove/add songs.
* Add "recent" sections: recent folders, recent playlists, recent songs.

### Known issues

* `tmux` subpanels may cause the application dimensions to be incorrect.

### Reports and Debugging

The application uses a log file located at `~/.cplayer/logfile.log` to report and debug errors. The log file contains
detailed information about all errors that occur while the application is running, including the time and date of the
error, the error message, and the stack trace.

To view the log file, you can use a text editor or a terminal emulator, e.g.:

```bash
tail -f ~/.cplayer/logfile.log
```

The log file can be used to report and debug errors.

### Developers

This project use [tox](https://tox.wiki/en/latest/) and [pytest](https://docs.pytest.org/) to run the library tests.

#### Dependencies

To use development tools you must install the poetry packages:

```bash
poetry install --with dev
```

#### Set up pre-commit

After cloning the repository run the following command in the repository root, this ensures that library tests are run
before each commit into the repository to maintain the quality of the project:

```bash
git config core.hooksPath .githooks
```

#### Basic configuration

Install development python requirements

```bash
poetry install
```

#### Testing

Simply run "`tox`" to execute all the library tests.

```bash
poetry run tox
```

To run the tests for a particular Python version, you can do:


```bash
poetry run tox -e py38
```

To clean the test environment:

```bash
poetry run tox -e clean
```

To publish the pypi package:

```bash
poetry run tox -e publish
```

#### Advanced configuration

By default `tox` will look for the python versions available on the system, and will run the compatibility tests on
the detected ones, and skip the versions not found. To ensure that compatibility tests are run for all Python
versions, the following steps must be followed:

1. Install [pyenv](https://github.com/pyenv/pyenv)
2. Install python versions:

    ```bash
    for python_version in "3.10" "3.11" "3.12"; do pyenv install ${python_version}; done
    ```

3. Enable python versions:

    ```bash
    pyenv local "3.10" "3.11" "3.12"
    ```

#### Static code analysis tools

These are the static code analysis tools that will help us to follow good practices and style guides of our source code.
We will be using the following tools, which will be executed when generating a new push in the repository (git hooks).

### Python static code analysis tools

The tools used are:

* [ruff](https://github.com/astral-sh/ruff): An extremely fast Python linter and code formatter, written in Rust.

  Tools executed by Ruff:

  * [pycodestyle](https://github.com/PyCQA/pycodestyle): Pycodestyle is a tool to check your Python code against some
    of the style conventions in [PEP 8](https://peps.python.org/pep-0008/).
  * [ruff-format](https://github.com/astral-sh/ruff/blob/main/docs/formatter.md#black-compatibility): The formatter
    is designed to be a drop-in replacement for [Black](https://github.com/psf/black).
  * [flake8](https://github.com/PyCQA/flake8): Flake8 is a python tool that glues together pycodestyle, pyflakes,
    and third-party plugins to check the style and quality of some python code.
  * [pydocstyle](https://github.com/PyCQA/pydocstyle): Pydocstyle is a static analysis tool for checking compliance
    with [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
  * [isort](https://pycqa.github.io/isort/): Python utility / library to sort imports alphabetically, and automatically
    separated into sections and by type.
  * [mccabe](https://github.com/PyCQA/mccabe): Complexity checker.
  * [bandit](https://github.com/PyCQA/bandit): Bandit is a tool designed to find common security issues.
  * [tryceratops](https://github.com/guilatrova/tryceratops): A linter to prevent exception handling antipatterns in
    Python.

* [prospector](https://github.com/PyCQA/prospector): Prospector is a tool to analyze Python code and output information
  about errors, potential problems, convention violations and complexity.

  Tools executed by Prospector:
  * [pylint](https://github.com/PyCQA/pylint): Pylint is a Python static code analysis tool which looks for programming
    errors, helps enforcing a coding standard, sniffs for code smells and offers simple refactoring suggestions.
  * [dodgy](https://github.com/landscapeio/dodgy): It is a series of simple regular expressions designed to detect
    things such as accidental SCM diff checkins, or passwords or secret keys hard coded into files.
  * [mypy](https://github.com/python/mypy): Mypy is an optional static type checker for Python.
  * [pyroma](https://github.com/regebro/pyroma): Pyroma is a product aimed at giving a rating of how well a Python
    project complies with the best practices of the Python packaging ecosystem, primarily PyPI, pip, Distribute etc,
    as well as a list of issues that could be improved.

### Run manually

```bash
bash .githooks/pre-commit
```

## License

[MIT](./LICENSE)
