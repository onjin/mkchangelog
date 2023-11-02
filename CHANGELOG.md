# Changelog

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

- **renderers:** rst-output: bold sections are generated wrongly without a space after bold marker

## v1.2.1 (2023-11-02)

### Fixes

- **parser:** allow any characters in summary (first line)
- **renderers:** empty HEAD sections should not be rendered in CHANGELOG

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

## v1.0.2 (2023-10-25)

### Fixes

- **core:** make project working with python 3.7 and 3.12

## v1.0.1 (2023-10-25)

### Fixes

- **bump:** proper Version sorting

## v1.0.0 (2023-10-25)

### Refactors

- **core:** use optional rich for colorized output
