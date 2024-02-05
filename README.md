# mkchangelog

<div align="center">

|         |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| CI/CD   | [![CI - Test](https://github.com/onjin/mkchangelog/actions/workflows/test.yml/badge.svg)](https://github.com/onjin/mkchangelog/actions/workflows/test.yml)                                                                                                                                                                                                                                                                                                                                       |
| Package | [![PyPI - Version](https://img.shields.io/pypi/v/mkchangelog.svg?logo=pypi&label=PyPI&logoColor=gold)](https://pypi.org/project/mkchangelog/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/mkchangelog.svg?color=blue&label=Downloads&logo=pypi&logoColor=gold)](https://pypi.org/project/mkchangelog/) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mkchangelog.svg?logo=python&label=Python&logoColor=gold)](https://pypi.org/project/mkchangelog/)                 |
| Meta    | [![linting - Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![code style - Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![types - Mypy](https://img.shields.io/badge/types-Mypy-blue.svg)](https://github.com/python/mypy) [![License - MIT](https://img.shields.io/badge/license-MIT-9400d3.svg)](https://spdx.org/licenses/) |

</div>

---

The CHANGELOG.md generator from git log using the [`conventional commits`](https://www.conventionalcommits.org/en/v1.0.0/) scheme.

Example generated changelog: [CHANGELOG.md](CHANGELOG.md)

**Table of Contents**

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Features](#features)
- [License](#license)

## Installation

```console
pip install mkchangelog
```

## Usage

The list of versions is taken from list of signed git tags detected by prefix (default `v`, f.e. `v1.3.4`).

### Generate changelog

To generate changelog for current and all previous versions (signed tags) to CHAGELOG.md (default):

```console
$ mkchangelog generate       # Creates CHANGELOG.md
$ mkchangelog g              # Creates CHANGELOG.md
$ mkchangelog g --stdout     # Prints changelog to stdout
$ mkchangelog g --help       # Prints help for generate command
```

### Generate commit message

```console
$ mkchangelog commit         # Generates message.txt
$ mkchangelog c              # Generates message.txt
$ git commit -F message.txt  # Use message.txt as commit message
```

### Bump version

Interactive tool to:

- generate changelog
- calculate next version from feat/fix/breaking changes commits
- commit changelog and tag version

```console
$ mkchangelog bump           # Bumps next version
$ mkchangelog b              # Bumps next version
```

### Manage configuration

You can change default configuration using `.mkchangelog` (ini format) file in current directory.

```console
$ mkchangelog settings       # Shows current config as jon
$ mkchangelog s              # Shows current config as jon
$ mkchangelog s --generate   # Prints default config ini file
```

## Configuration

Default configuration is:

```ini

[GENERAL]
output = CHANGELOG.md                   ; output file
template = markdown                     ; template to use
commit_limit = 100                      ; commits limit per release (version)
unreleased = False                      ; include unreleased changes (HEAD...last_version)
unreleased_version = Unreleased         ; title of unreleased changes (f.e. next version v3.0.0)
hide_empty_releases = False             ; hide releases with no gathered commits
changelog_title = Changelog             ; Changelog title
commit_types_list = fix,feat            ; list of commit types to include in Changelog
commit_type_default_priority = 10       ; default priority of commit type, for Changelog ordering
tag_prefix = v                          ; versions tag prefix to detect/generate git tags

[commit_types]                          ; valid commit types (for `--commit-types all`) and their names
build = Build
chore = Chore
ci = CI
dev = Dev
docs = Docs
feat = Features
fix = Fixes
perf = Performance
refactor = Refactors
style = Style
test = Test
translations = Translations

[commit_types_priorities]               ; custom commit types priorities, for Changelog ordering
feat = 40
fix = 30
refactor = 20
```

## Features

### Creates changelog from git log

- the list of releases is created from list of annotated git tags matching configured `tag_prefix`.
- the unreleased changes are included if `unreleased` is `true`.
- from git log messages matching configured `commit_types` are parsed and grouped by the type.
- certain groups (types) are sorted by configured `commit_types_priorities`.
- only configured `commit_types_list` types are rendered, if not `--commit-types [type,type, | all]` was provided

### Includes additional git commits from text files

- additional commit files (`*.txt`) can be put at `.mkchangelog.d/versions/<version>/commits/` directory

For example:

- [v1.0.3/commits](https://github.com/onjin/mkchangelog/blob/master/.mkchangelog.d/versions/v1.0.3/commits/)

### Built-in templates

The `mkchangelog` includes a few builtin changelog output formats

```console
$ mkchangelog g --template markdown
$ mkchangelog g --template rst
$ mkchangelog g --template json
```

### Custom `header` and `footer` per version [for built-in templates]

The `header` and `footer` files are included from files:

- .mkchangelog.d/versions/<version>/header
- .mkchangelog.d/versions/<version>/footer

For example:

- [v1.0.3/header](https://github.com/onjin/mkchangelog/blob/master/.mkchangelog.d/versions/v1.0.3/header)
- [v1.0.3/footer](https://github.com/onjin/mkchangelog/blob/master/.mkchangelog.d/versions/v1.0.3/footer)

### Custom [jinja](https://jinja.palletsprojects.com/en/3.1.x/) templates

You can create your own templates and pass them by `--template` parameter of `mkchangelog generate`
or set it in `.mkchangelog` configuration file.

**Using configuration file**

```dosini
[GENERAL]
...
# put `custom_template.jinja` in `.mkchangelog.d/templates/
template = custom_template.jinja

# or specify full path to template
template = ./path/to/template.jinja
...
```

**Using `--template` parameter\***

```console
# put `custom_template.jinja` in `.mkchangelog.d/templates/
$ mkchangelog g --template custom_template.jinja

# or specify full path to template
$ mkchangelog g --template ./path/to/template.jinja
```

Refer to built-in templates for examples:

- [markdown.jinja2](https://github.com/onjin/mkchangelog/blob/master/mkchangelog/templates/markdown.jinja2)
- [rst.jinja2](https://github.com/onjin/mkchangelog/blob/master/mkchangelog/templates/rst.jinja2)

### Template filters

Apart from builtin jinja2 filter there are additional custom filters:

- `underline` - f.e. `{{ changelog.title | underline('=') }}`
- `regex_replace` - f.e. `{{ "line with #12 issue ref" | regex_replace("#(\d+)", "#ISSUE-\\1") }}`

You can create and register your own filters using **.mkchangelog.d/hooks.py** file.

Example implementation of hooks:

- https://github.com/onjin/mkchangelog/blob/master/.mkchangelog.d/hooks.py

### Your own commit types

The `commit_types` can be fully customized by `.mkchangelog` file.

```ini
[GENERAL]
commit_types_list = awesome
hide_empty_releases = True

[commit_types]
awesome = Best change
sad = Had to write it
not_sure = Works but why?

[commit_types_priorities]
awesome = 40
sad = 30
not_sure = 20

```

```console
$ mkchangelog g --commit_types all
$ mdless CHANGELOG.md
```

![image](https://github.com/onjin/mkchangelog/assets/44516/33f9b6dd-2860-437e-98be-d3a2e1819223)

### Plugins / hooks system

You can use hooks system to extend mkchangelog functionality.
All hooks are loaded from `.mkchangelog.d/hooks.py` file which must be a valid python module.

You can check the specification for available hooks at [hookspecs.py](https://github.com/onjin/mkchangelog/blob/master/mkchangelog/hookspecs.py) file.
The mkchangelog built-in hooks are implemented at [lib.py](https://github.com/onjin/mkchangelog/blob/master/mkchangelog/lib.py) file.

**Available hooks**:

- provide_template_filters - returns dictionary of jinja2 filters,
- provide_changelog_loglines_filter - returns functions which filters list of `LogLine` - you can use it to filter out f.e. some scopes

**Example .mkchangelog.d/hooks.py**

```python

from __future__ import annotations

import random
from typing import Any, Callable, Dict, List

from mkchangelog.config import Settings
from mkchangelog.lib import hookimpl


def fancylize(s):
    return "".join([c.lower() if random.randint(0, 1) else c.upper() for c in s])


@hookimpl
def provide_template_filters(settings: Settings) -> Dict[str, Callable[[Any], str]]:  # noqa
    """Add 'fancylize' jinja2 template filter"""
    return {"fancylize": fancylize}


@hookimpl
def provide_changelog_loglines_filter(settings: Settings) -> Callable[[List[LogLine]], List[LogLine]]:
    """Hide lines with scope 'hidden_scope'"""
    return lambda loglines: [line for line in loglines if line.scope != "hidden_scope"]

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
