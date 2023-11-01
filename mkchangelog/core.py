from __future__ import annotations

from collections import Counter
from datetime import datetime, tzinfo
from itertools import groupby
from operator import attrgetter
from typing import TYPE_CHECKING, Dict, Iterable, List, Optional

import semver

from mkchangelog.models import Changelog, ChangelogSection, CommitType, LogLine, Version
from mkchangelog.parser import GitMessageParser
from mkchangelog.providers import LogProvider, VersionsProvider
from mkchangelog.utils import create_version

if TYPE_CHECKING:
    pass

TZ_INFO: Optional[tzinfo] = datetime.now().astimezone().tzinfo
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
DEFAULT_MAX_GIT_LOG = 1000


def get_next_version(tag_prefix: str, current_version: str, commits: list[LogLine]) -> Optional[Version]:
    """Return next version or None if not available

    Args:
        tag_prefix (str): version tags prefix
        current_version (str): current version, f.i. v1.1.1
        commits (list): list of LogLine containing commits till current version

    Returns:
        Version | None - next version object or None if no new version is available.
    """
    next_version = create_version(tag_prefix, current_version)
    current_version = str(next_version)

    # count types
    types: dict[str, int] = Counter()
    for commit in commits:
        types[commit.commit_type] += 1
        if commit.breaking_change:
            types["breaking_changes"] += 1

    # bump version
    breaking_changes: int = types.get("breaking_changes", 0)
    if breaking_changes > 0:
        next_version = next_version.bump_major()
    elif "feat" in types.keys():
        next_version = next_version.bump_minor()
    elif "fix" in types.keys():
        next_version = next_version.bump_patch()

    # make next version
    if semver.VersionInfo.parse(current_version).compare(next_version) == 0:
        return None
    name = f"{tag_prefix}{next_version!s}"

    return Version(name=name, date=datetime.now(tz=TZ_INFO), semver=next_version)


def group_commits_by_type(commits: Iterable[LogLine]) -> Dict[str, Iterable[LogLine]]:
    return groupby(
        sorted(commits, key=lambda x: x.commit_type),
        attrgetter("commit_type"),
    )


class ChangelogGenerator:
    def __init__(
        self, log_provider: LogProvider, versions_provider: VersionsProvider, message_parser: GitMessageParser
    ):
        self.log_provider = log_provider
        self.versions_provider = versions_provider
        self.message_parser = message_parser

    def get_loglines(self, commits: list[str], *, strict=False) -> List[LogLine]:
        lines: list[LogLine] = []
        for msg in commits:
            try:
                lines.append(self.message_parser.parse(msg))
            except ValueError:
                if strict:
                    raise
        return lines

    def get_changelog_section(
        self,
        *,
        from_version: Optional[Version] = None,
        to_version: Optional[Version] = None,
        commit_types: Optional[list[CommitType]] = None,
        max_count: int = DEFAULT_MAX_GIT_LOG,
    ) -> ChangelogSection:
        if from_version is None:
            from_version = Version(name="HEAD", date=datetime.now(tz=TZ_INFO), semver=None)
        rev = from_version.name
        if to_version:
            rev = f"{rev}...{to_version.name}"
        messages: List[str] = list(self.log_provider.get_log(max_count=max_count, rev=rev))
        log_lines: List[LogLine] = []
        log_lines = self.get_loglines(messages)

        # filter by commit_types
        if commit_types:
            # TODO: support list of internal types, `all` for all internal types and `any` to allow any type
            log_lines = [line for line in log_lines if line.commit_type in commit_types or "all" in commit_types]
        reverts = [line for line in log_lines if line.commit_type == "revert"]
        breaking_changes = [line for line in log_lines if line.breaking_change is True]

        if not log_lines:
            return ChangelogSection(version=from_version)

        section = ChangelogSection(
            version=from_version,
            changes={
                commit_type: sorted(changes, key=lambda i: i.scope if i.scope else "")
                for commit_type, changes in group_commits_by_type(log_lines)
            },
            reverts=reverts,
            breaking_changes=breaking_changes,
        )
        return section

    def get_changelog(
        self,
        commit_types: Optional[list[CommitType]] = None,
    ) -> Changelog:
        head = Version(name="HEAD", date=datetime.now(tz=TZ_INFO), semver=None)
        versions: list[Version] = [head, *self.versions_provider.get_versions()]
        if len(versions) == 1:
            # just head -> all
            return Changelog(sections=[self.get_changelog_section(from_version=versions[0], commit_types=commit_types)])

        sections: list[ChangelogSection] = []
        while len(versions) > 1:
            sections.append(
                self.get_changelog_section(from_version=versions[0], to_version=versions[1], commit_types=commit_types)
            )
            versions = versions[1:]
        sections.append(self.get_changelog_section(from_version=versions[0], commit_types=commit_types))
        return Changelog(sections=sections)
