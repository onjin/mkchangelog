# mkchangelog

<div align="center">

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CI/CD   | [![CI - Test](https://github.com/onjin/mkchangelog/actions/workflows/test.yml/badge.svg)](https://github.com/onjin/mkchangelog/actions/workflows/test.yml)                                                                                                                                                                                                                                                                                                                                       |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/mkchangelog.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/mkchangelog/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/mkchangelog.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/mkchangelog/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkchangelog.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/mkchangelog/)                 |
| Meta    | [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) |

</div>

---

Use this CLI tool to create a changelog for a project from the git log using the [`conventional commits`](https://www.conventionalcommits.org/en/v1.0.0/) scheme.

Features:

- show the last changes as Markdown, ReStructuredText or Json
- generate full CHANGELOG.[md,rst,json] file
- compute and bump next versions (using `semver`)
- group changes by `type` and by `scope` also
- aggregate `Closes: XXX-XX[,YYY-YY]` and `Relates: XXX-XX[,YYY-YY]` footer references

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Installation

```console
pip install mkchangelog
pip install mkchangelog[colors]  # for console colorized output
```

## Usage

```console
mkchangelog changes - show  changelog for last changes, using default `fix` and `feat` types only
mkchangelog changes -t all - show  changelog for last changes, using all types
mkchangelog generate -t all - generate full changelog for current and all previous versions (signed tags) on the screen
mkchangelog bump - interactive tool; compute next versions from `feat`, `fix` and `breaking_changes`, optionaly write `CHANGELOG.md`, commit and tag next version
```

## Contributing

Install `pre-commit`

```python
pip install pre-commit
pre-commit install
```

### Run tests

```console
hatch run all:test
```

### Linting

```console
hatch run lint:all
```

## License

`mkchangelog` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
