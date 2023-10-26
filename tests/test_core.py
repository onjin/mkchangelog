from dataclasses import dataclass
from typing import ClassVar, Dict, Generator, Optional

from mkchangelog.core import ChangelogGenerator, get_next_version
from mkchangelog.models import ChangelogSection, CommitType, LogLine, Version


class MockLogParser:
    def __init__(self, log: Optional[list[LogLine]] = None, versions: Optional[list[Version]] = None):
        self._log = log or []
        self._versions = versions or []

    def get_versions(self, tag_prefix: str, limit: Optional[int] = None) -> list[Version]:  # noqa: ARG002
        return self._versions

    def get_last_version(self, tag_prefix: str) -> Optional[Version]:  # noqa: ARG002
        return self._versions[0] if self._versions else None

    def get_log(
        self, max_count: int = 1000, rev: Optional[str] = None, types: Optional[list[str]] = None  # noqa: ARG002
    ) -> Generator[LogLine, None, None]:
        return (line for line in self._log)


def test_next_version_for_breaking_changes():
    # Given - current version and commits with breaking changes
    current_version = "v1.2.3"
    commits = [
        LogLine(
            subject="feat(api): some",
            message="feat(api): some\n\nBREAKING CHANGES: API broken\nbadly\n\n",
            revert=False,
            commit_type="feat",
            scope="(api)",
            title="some",
            references=[],
            breaking_change=["API broken"],
        )
    ]

    # When - we get next version
    version = get_next_version("v", current_version, commits)

    # Then - major segment is bumped
    assert version is not None
    assert version.name == "v2.0.0", version


def pytest_generate_tests(metafunc):
    # called once per each test function
    if not metafunc.cls:
        return
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist])


class TestChangelogGenerator(object):
    @dataclass
    class ParamsForChangelogSection(object):
        input_log: list[LogLine]
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
                        LogLine(
                            subject="",
                            message="feat(scope): xyz feat",
                            commit_type="feat",
                            title="xyz feat",
                            scope="scope",
                        ),
                        LogLine(
                            subject="",
                            message="feat(scope): abc feat",
                            commit_type="feat",
                            title="abc feat",
                            scope="scope",
                        ),
                        LogLine(
                            subject="",
                            message="fix(scope): xyz fix",
                            commit_type="fix",
                            title="xyz fix",
                            scope="scope",
                        ),
                        LogLine(
                            subject="",
                            message="fix(scope): abc fix",
                            commit_type="fix",
                            title="abc fix",
                            scope="scope",
                        ),
                    ],
                    input_versions=["1.1.1"],
                    output_version="HEAD",
                    output_changes={
                        CommitType.FEAT: [
                            LogLine(
                                subject="",
                                message="feat(scope): xyz feat",
                                commit_type="feat",
                                title="xyz feat",
                                scope="scope",
                            ),
                            LogLine(
                                subject="",
                                message="feat(scope): abc feat",
                                commit_type="feat",
                                title="abc feat",
                                scope="scope",
                            ),
                        ],
                        CommitType.FIX: [
                            LogLine(
                                subject="",
                                message="fix(scope): xyz fix",
                                commit_type="fix",
                                title="xyz fix",
                                scope="scope",
                            ),
                            LogLine(
                                subject="",
                                message="fix(scope): abc fix",
                                commit_type="fix",
                                title="abc fix",
                                scope="scope",
                            ),
                        ],
                    },
                )
            },
        ]
    }

    def test_get_changelog_section(self, parameters: ParamsForChangelogSection):
        section = ChangelogGenerator(
            parser=MockLogParser(log=parameters.input_log, versions=parameters.input_versions)
        ).get_changelog_section()
        assert isinstance(section, ChangelogSection)
        assert section.version == parameters.output_version
        assert section.changes == parameters.output_changes
