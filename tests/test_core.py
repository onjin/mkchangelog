from __future__ import annotations

import contextlib
from dataclasses import dataclass
from typing import ClassVar, Dict, Generator, List, Optional

import pytest

from mkchangelog.config import Settings, get_settings
from mkchangelog.core import ChangelogGenerator, get_next_version
from mkchangelog.models import Changelog, ChangelogSection, CommitType, LogLine, Version
from mkchangelog.parser import GitMessageParser
from mkchangelog.providers import LogProvider, VersionsProvider


def pytest_generate_tests(metafunc):
    # called once per each test function
    if not metafunc.cls:
        return
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist])


parser = GitMessageParser(Settings())


def log_line(message: str) -> LogLine:
    return parser.parse(message)


def log_lines(messages: List[str]) -> List[LogLine]:
    lines: List[LogLine] = []
    for msg in messages:
        with contextlib.suppress(ValueError):
            lines.append(log_line(msg))
    return lines


GIT_LOG = [
    "fix: upgrade deprecated sermer.parse",
    "feat(core): add `ChangelogGenerator.get_changelog()` method",
    "refactor: organize code for `parser` and `renderer` (output)",
    "doc(README.md): add build status badge",
    "ci(github): install missing `hatch` to run tests",
    "ci(github): add test workflow",
    "refactor: simplify commands",
    "chore(changelog): write CHANGELOG.md for version v1.1.0",
    "build: bump version to 1.1.0",
    "feat(bump): allow to `--set-versions x.y.z` to force next version",
    "refactor(core): split code into parser/output/main modules",
    "cli: fix prog directire to show that the script name is mkchangelog",
    "chore: bump version to update broken github links at pypi",
    "docs: add usage info, and fix github links",
    "chore(build): fix hatch env matrix",
    "chore(changelog): write CHANGELOG.md for version v1.0.2",
    "fix(core): make project working with python 3.8 and 3.12",
    "chore: bump package version",
    "chore: remove obsolete CHANGELOG.txt in favor of generated CHANGELOG.md",
    "chore(changelog): write CHANGELOG.md for version v1.0.1",
    "fix(bump): proper Version sorting",
    "build: bump version to 1.0.0",
    "refactor(core): use optional rich for colorized output",
    "build: initial commit",
]
"""
build = 3
chore = 7
ci = 2
cli = 1
doc = 1
docs = 1
feat = 2
fix = 3
refactor = 4
"""


class MockVersionsProvider(VersionsProvider):
    def __init__(self, versions: Optional[list[Version]] = None):
        self._versions = versions or []

    def get_versions(self, limit: Optional[int] = None) -> list[Version]:  # noqa: ARG002
        return self._versions

    def get_last_version(self) -> Optional[Version]:
        return self._versions[0] if self._versions else None


class MockLogProvider(LogProvider):
    def __init__(self, log: Optional[list[str]] = None, versions: Optional[list[Version]] = None):
        self._log = log or []
        self._versions = versions or []

    def get_log(
        self,
        commit_limit: int = 1000,  # noqa: ARG002
        rev: Optional[str] = None,  # noqa: ARG002
        types: Optional[list[str]] = None,  # noqa: ARG002
    ) -> Generator[LogLine, None, None]:
        return self._log


@pytest.mark.parametrize(
    "current_version,commits,next_version",
    [
        ("v1.2.3", ["feat(api): some\n\nBREAKING CHANGE: API broken\nbadly\n\n"], "v2.0.0"),
        ("v1.2.4", ["feat(api)!: break indicator"], "v2.0.0"),
    ],
)
def test_next_version_for_breaking_changes(current_version: str, commits: list[str], next_version: str):
    # Given - current version and commits with breaking changes
    commits: List[LogLine] = [log_line(message) for message in commits]

    # When - we get next version
    version = get_next_version("v", current_version, commits)

    # Then - major segment is bumped
    assert version.name == next_version, version


class TestChangelogGenerator(object):
    @dataclass
    class ParamsForChangelog(object):
        input_log: list[str]
        input_versions: list[Version]
        output_versions: list[str]
        output_changes: Dict[str, Dict[CommitType, list[LogLine]]]

    @dataclass
    class ParamsForChangelogSection(object):
        input_log: list[str]
        input_versions: list[Version]
        output_version: str
        output_changes: Dict[CommitType, list[LogLine]]

    params: ClassVar = {
        "test_get_changelog_section": [
            {
                "parameters": ParamsForChangelogSection(
                    input_log=[], input_versions=[], output_version="HEAD", output_changes={}
                )
            },
            {
                "parameters": ParamsForChangelogSection(
                    input_log=[
                        "feat(scope): xyz feat",
                        "feat(scope): abc feat",
                        "fix(scope): xyz fix",
                        "fix(scope): abc fix",
                    ],
                    input_versions=["1.1.1"],
                    output_version="HEAD",
                    output_changes={
                        "Features": log_lines(
                            [
                                "feat(scope): xyz feat",
                                "feat(scope): abc feat",
                            ]
                        ),
                        "Fixes": log_lines(
                            [
                                "fix(scope): xyz fix",
                                "fix(scope): abc fix",
                            ]
                        ),
                    },
                )
            },
        ],
        "test_get_changelog": [
            {
                "parameters": ParamsForChangelog(
                    input_log=[], input_versions=[], output_versions=["HEAD"], output_changes={"HEAD": {}}
                )
            },
            {
                "parameters": ParamsForChangelog(
                    input_log=GIT_LOG,
                    input_versions=[],
                    output_versions=["HEAD"],
                    output_changes={
                        "HEAD": {
                            "Build": log_lines(
                                [
                                    "build: bump version to 1.1.0",
                                    "build: bump version to 1.0.0",
                                    "build: initial commit",
                                ]
                            ),
                            "Chore": log_lines(
                                [
                                    "chore: bump version to update broken github links at pypi",
                                    "chore: bump package version",
                                    "chore: remove obsolete CHANGELOG.txt in favor of generated CHANGELOG.md",
                                    "chore(build): fix hatch env matrix",
                                    "chore(changelog): write CHANGELOG.md for version v1.1.0",
                                    "chore(changelog): write CHANGELOG.md for version v1.0.2",
                                    "chore(changelog): write CHANGELOG.md for version v1.0.1",
                                ]
                            ),
                            "CI": log_lines(
                                [
                                    "ci(github): install missing `hatch` to run tests",
                                    "ci(github): add test workflow",
                                ]
                            ),
                            "Docs": log_lines(
                                [
                                    "docs: add usage info, and fix github links",
                                ]
                            ),
                            "Features": log_lines(
                                [
                                    "feat(bump): allow to `--set-versions x.y.z` to force next version",
                                    "feat(core): add `ChangelogGenerator.get_changelog()` method",
                                ]
                            ),
                            "Fixes": log_lines(
                                [
                                    "fix: upgrade deprecated sermer.parse",
                                    "fix(bump): proper Version sorting",
                                    "fix(core): make project working with python 3.8 and 3.12",
                                ]
                            ),
                            "Refactors": log_lines(
                                [
                                    "refactor: organize code for `parser` and `renderer` (output)",
                                    "refactor: simplify commands",
                                    "refactor(core): split code into parser/output/main modules",
                                    "refactor(core): use optional rich for colorized output",
                                ]
                            ),
                        }
                    },
                )
            },
        ],
    }

    def test_get_changelog_section(self, parameters: ParamsForChangelogSection):
        section = ChangelogGenerator(
            settings=get_settings(),
            log_providers=[MockLogProvider(log=parameters.input_log)],
            versions_provider=MockVersionsProvider(versions=parameters.input_versions),
            message_parser=GitMessageParser(Settings()),
        ).get_changelog_section()
        assert isinstance(section, ChangelogSection)
        assert section.version.name == parameters.output_version
        assert section.changes == parameters.output_changes

    def test_get_changelog(self, parameters: ParamsForChangelog):
        generator = changelog = ChangelogGenerator(
            settings=get_settings(),
            log_providers=[MockLogProvider(log=parameters.input_log)],
            versions_provider=MockVersionsProvider(versions=parameters.input_versions),
            message_parser=GitMessageParser(Settings()),
        )
        changelog = generator.get_changelog(unreleased=True)
        assert isinstance(changelog, Changelog)
        sections = (sec for sec in changelog.sections)
        for version_name in parameters.output_versions:
            section = next(sections)
            assert section.version is not None
            assert section.version.name == version_name
            assert len(section.changes.keys()) == len(parameters.output_changes[version_name].keys())
            for commit_type in section.changes.keys():
                assert section.changes[commit_type] == parameters.output_changes[version_name][commit_type], commit_type
