# Changelog

## v2.3.2 (2024-02-01)

### Fixes

- **python:** drop support for *Python 3.7*

## v2.3.1 (2024-02-01)

### Fixes

- **templates:** Add missing new line between items

## v2.3.0 (2024-01-20)

### Features

- **parser:** render footer references in text format Closes: #7

### Fixes

- **commands:** by default print just message on errors, use `-e/--raise-exceptions` to raise exception instead

## v2.2.0 (2023-11-23)

### Features

- **providers:** add `FileLogProvider` to add custom/external commits from files, per version

### Fixes

- **settings:** use commit types from .mkchanelog in `mkchangelog commit` also

## v2.1.1 (2023-11-08)

### Fixes

- **versioning:** support also short versions like `v1` or `v1.1`

## v2.1.0 (2023-11-06)

### Features

- **renderers:** support custom version's header & footer

### Fixes

- **config:** make argparse store_true not overwrite .mkchangelog settings

## v2.0.0 (2023-11-05)

### ⚠ BREAKING CHANGES
- 'mkchangelog generate' now writes to file as default. Use '--stdout' to print changelog.

### Features

- more consistent settings, CLI parameters, and commands name and behavior BREAKING CHANGE: 'mkchangelog generate' now writes to file as default. Use '--stdout' to print changelog.

## v1.7.0 (2023-11-05)

### Features

- **generate:** add `--skip-empty` to skip empty versions from changelog (with not commits for selected types)

## v1.6.0 (2023-11-05)

### Features

- **config:** add `mkchangelog config` command to generate or peek parsed config
- **generate:** add `--include-unreleased` and `--unreleased-name NAME` options

### Fixes

- **commit:** help message for `mkchangelog commit --stdout` option

## v1.5.0 (2023-11-03)

### Features

- **renderers:** add `template` renderer and `--template` option to point to own `jinja` template to generate Changelog

## v1.4.0 (2023-11-02)

### Features

- **commands:** add `mkchangelog commit` command to generate proper commit message

### Refactors

- **commands:** remove `changes` command, now it was mostly duplicating the `generate` command
- **renderers:** change date forma to iso date

## v1.3.0 (2023-11-02)

### Features

- **config:** add support for reading config from config file .mkchangelog (#4)
- **renderers:** add `BREAKING CHANGES:` section to rendered changelog

### Fixes

- **renderers:** rst-output: bold sections are generated wrongly without a space after bold marker Closes: #9

## v1.2.1 (2023-11-02)

### Fixes

- **parser:** allow any characters in summary (first line)
- **renderers:** empty HEAD sections should not be rendered in CHANGELOG Closes: #6

## v1.2.0 (2023-11-01)

### Features

- **core:** add `ChangelogGenerator.get_changelog()` method
- **renderers:** add `json` and `rst` renderers

### Fixes

- upgrade deprecated sermer.parse
- **config:** add `max_size` parameter to `lru_cache` for python `3.7`

### Refactors

- organize code for `parser` and `renderer` (output)
- simplify commands

## v1.1.0 (2023-10-25)

### Features

- **bump:** allow to `--set-versions x.y.z` to force next version

### Refactors

- **core:** split code into parser/output/main modules

## v1.0.3 (2023-10-25)

This release had only `Chore` and `Docs` changes,
so with my config `commit_types_list = fix,feat,refactor` this
version release notes are empty.

And this message comes from `.mkchangelog.d/versions/v1.0.3/header` file.

### Features

- **providers:** Artifical / external commits provider

Apart from custom version header you can also put footer (under all version changes)
by creating `.mkchangelog.d/versions/v1.0.3/footer` :).

## v1.0.2 (2023-10-25)

### Fixes

- **core:** make project working with python 3.7 and 3.12

## v1.0.1 (2023-10-25)

### Fixes

- **bump:** proper Version sorting

## v1.0.0 (2023-10-25)

### Refactors

- **core:** use optional rich for colorized output
