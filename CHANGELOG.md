# Changelog

## v1.2.0 (2023-11-01 22:58:25+01:00)

### Features

* **core:**add `ChangelogGenerator.get_changelog()` method
* **renderers:**add `json` and `rst` renderers

### Fixes

* upgrade deprecated sermer.parse
* **config:**add `max_size` parameter to `lru_cache` for python `3.7`

### Refactors

* organize code for `parser` and `renderer` (output)
* simplify commands

### Chore

* clean up unused `--cli` option
* **release:**bump version to v1.2.0

### CI

* **github:**install missing `hatch` to run tests
* **github:**add test workflow


## v1.1.0 (2023-10-25 23:04:39+02:00)

### Features

* **bump:**allow to `--set-versions x.y.z` to force next version

### Refactors

* **core:**split code into parser/output/main modules

### Build

* bump version to 1.1.0

### Chore

* **changelog:**write CHANGELOG.md for version v1.1.0


## v1.0.3 (2023-10-25 11:54:05+02:00)

### Chore

* bump version to update broken github links at pypi
* **build:**fix hatch env matrix
* **changelog:**write CHANGELOG.md for version v1.0.2
* **changelog:**write CHANGELOG.md for version v1.0.2

### Docs

* add usage info, and fix github links


## v1.0.2 (2023-10-25 11:37:54+02:00)

### Fixes

* **core:**make project working with python 3.7 and 3.12

### Chore

* bump package version
* remove obsolete CHANGELOG.txt in favor of generated CHANGELOG.md
* **changelog:**write CHANGELOG.md for version v1.0.2


## v1.0.1 (2023-10-25 11:11:46+02:00)

### Fixes

* **bump:**proper Version sorting

### Chore

* **changelog:**write CHANGELOG.md for version v1.0.1


## v1.0.0 (2023-10-25 11:09:45+02:00)

### Refactors

* **core:**use optional rich for colorized output

### Build

* bump version to 1.0.0
* initial commit
