# mkchangelog

[![PyPI - Version](https://img.shields.io/pypi/v/mkchangelog.svg)](https://pypi.org/project/mkchangelog)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkchangelog.svg)](https://pypi.org/project/mkchangelog)

-----

Use this CLI tool to create a changelog for a project from the git log using the `conventional commits` scheme.

Features:
- show the last changes as markdown
- generate full CHANGELOG.md file
- compute and bump next versions (using `semver`)
- group changes by `type` and by `scope` also
- aggregate `Closes XXX-XX[,YYY-YY]` and `Relates XXX-XX[,YYY-YY]` references
- optionally output colorized markdown to the console (install by `mkchangelog[colors]` and add `--cli` option)

**Table of Contents**

- [Installation](#installation)
- [Uusage](#usage)
- [License](#license)

## Installation

```console
pip install mkchangelog
```

## Usage

```console
mkchangelog changes - show  changelog for last changes, using default `fix` and `feat` types only
mkchangelog changes -t all - show  changelog for last changes, using all types
mkchangelog generate -t all - generate full changelog for current and all previous versions (signed tags) on the screen
mkchangelog bump - interactive tool; compute next versions from `feat`, `fix` and `breaking_changes`, optionaly write `CHANGELOG.md`, commit and tag next version
```

## License

`mkchangelog` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
