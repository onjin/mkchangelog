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


**NOTE**: Since version `2.0.0` there are some significant changes:
- `mkchangelog generate` writes to `--output file` as default - use `--stdout` to write to stdout
- `mkchangelog config` commands was renamed to `mkchangelog settings`
- options in `.mkchangelog` along with `mkchangelog generate` options were changed to be more consistent, use `mkchangelog settings --generate` to get new config file
- the `mkchangelog generate` options `--renderer` and `--template` were merged as `--template [renderer name | path to template]`

For other parameters changes refer to [usage](#usage) section.

## Features:


Changelog generation `mkchangelog g[enerate]`:
- generate full CHANGELOG.[md,rst,txt,json] `mkchangelog generate --template <markdown | rst | txt | json | path/to/custom/template >`
- detect verions (releases) by git annotated tags (f.e. `git tag -am v1.0.0 v1.0.0` or use `mkchangelog bump`)
- limit included commit types `mkchangelog generate --commit-types feat,fix,refactor`
- group commits by `type` and by `scope` also
- include unreleased changes section (`mkchangelog generate --unreleased`)
- custom jinja templates `--template ./path/to/template.jinja` - check [internal templates](https://github.com/onjin/mkchangelog/blob/master/mkchangelog/templates/)
- custom version's header & footer, in `.mkchangelog.d/versions/v1.0.3/header` and `.mkchangelog.d/versions/v1.0.3/footer`

Configuration generation `mkchangelog s[ettings]`:
- configure `mkchangelog` using `.mkchangelog` INI file (`mkchangelog settings --generate > .mkchangelog`)

Commit message helper `mkchangelog c[ommit]`:
- create `mkchangelog.txt` with proper commit message `mkchangelog commit [--stdout]`, then `git commit -F message.txt`

Bump version `mkchangelog b[ump]`:
- compute and bump next version (using `semver`), including generated `CHANGELOG`


Example generated changelog: [CHANGELOG.md](CHANGELOG.md)

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

To generate changelog for current and all previous versions (signed tags) to CHAGELOG.md (default):

```console
mkchangelog generate [--stdout] [--template <markdown | rst | json | ./tmpl.jinja >]
```

```console
❯ mkchangelog generate --help
usage: mkchangelog generate [-h] [-o OUTPUT] [-t TEMPLATE] [-l COMMIT_LIMIT] [-u] [-uv UNRELEASED_VERSION] [--hide-empty-releases]
                            [--changelog-title CHANGELOG_TITLE] [--tag-prefix TAG_PREFIX] [--commit-types COMMIT_TYPES_LIST [COMMIT_TYPES_LIST ...]]
                            [--stdout]

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file, default: CHANGELOG.md
  -t TEMPLATE, --template TEMPLATE
                        specify template to use [markdown, rst, json], or path to your template default: markdown
  -l COMMIT_LIMIT, --commit-limit COMMIT_LIMIT
                        number of commits to display per release, default: 100
  -u, --unreleased      include unreleased changes in changelog
  -uv UNRELEASED_VERSION, --unreleased-version UNRELEASED_VERSION
                        use specified version as unreleased release; default 'Unreleased'
  --hide-empty-releases
                        skip empty versions
  --changelog-title CHANGELOG_TITLE
                        changelog title, default 'Changelog'
  --tag-prefix TAG_PREFIX
                        version tag prefix; default 'v'
  --commit-types COMMIT_TYPES_LIST [COMMIT_TYPES_LIST ...]
                        f.e. feat,fix,refactor, all - for all convigured; default from 'commit_types_list' settings
  --stdout              output changelog to stdout
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

Experimental commands:

Interactive tool to generate changelog, bump version, commit changelog and tag version:

```console
mkchangelog bump ## The 'bump' commands gets same parameters as 'generate'
```

## Configuration

You can change default configuration using `.mkchangelog` (ini format) file in current directory.

```console
mkchangelog settings --generate  # generates default .mkchangelog file
```

```console
mkchangelog settings # shows current default settings merged with .mkchangelog settings
```

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
