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
- group changes by `type` and by `scope` also
- provide own template by `--renderer template --template ./path/to/template.jinja`
- compute and bump next versions (using `semver`)

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

The list of versions is taken from list of signed git tags detected by prefix (default `v`, f.e. `v1.3.4`).

To generate changelog for current and all previous versions (signed tags) on the screen:

```console
mkchangelog generate
```

To generate commit message use:

```console
$ mkchangelog commit --stdout
Git Commit Format: type(scope): summary

Commit Type [build,chore,ci,dev,docs,FEAT,fix,perf,refactor,style,test,translations]: feat
Scope: (optional): commands
Summary line: add `mkchangelog commit` command to generate proper commit message
Is breaking change? [y/N]
Long description (body): The message be displayed at stdout by passing `--stdout` parameter. Otherwise will be saved as `message.txt` file.
---
feat(commands): add `mkchangelog commit` command to generate proper commit message

The message be displayed at stdout by passing `--stdout` parameter. Otherwise will be saved as `message.txt` file.
---
```

Experimental (but works somehow) commands:

Interactive tool to generate changelog, bump version, commit changelog and tag version:

```console
mkchangelog bump - interactive tool; compute next versions from `feat`, `fix` and `breaking_changes`, optionaly write `CHANGELOG.md`, commit and tag next version
```

## Configuration

You can change default configuration using `.mkchangelog` (ini format) file in current directory.

Default configuration is:
```ini
[GENERAL]
changelog_title = Changelog         ; title of generated text changelog
commit_type_default_priority = 10   ; default priority for rendered commit types
default_renderer = markdown         ; default renderer (use `-r <renderer` to overwrite)
git_tag_prefix = v                  ; default git tag prefix for versions
short_commit_types_list = fix,feat  ; default list of commit types included in changelog (use `-t <type,type,.. | all>` to overwrite)

[commit_types]                      ; available commit prefixes along with their names used to render headers
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

[commit_types_priorities]           ; prioritize commit types to render them earlier, check `commit_type_default_priority`
feat = 40
fix = 30
refactor = 20

; vim: ft=ini
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
