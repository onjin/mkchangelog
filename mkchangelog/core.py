from __future__ import annotations

from collections import Counter
from datetime import datetime, tzinfo
from itertools import groupby, tee
from operator import attrgetter
from typing import TYPE_CHECKING, Iterator, Optional

import semver

from mkchangelog.models import TYPES_ORDERING, Changelog, ChangelogSection, CommitType, LogLine, Version
from mkchangelog.parser import LogParser
from mkchangelog.utils import create_version

if TYPE_CHECKING:
    from git import Commit

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
            types["breaking_change"] += 1

    # bump version
    breaking_change: int = types.get("breaking_change", 0)
    if breaking_change > 0:
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


def group_commits_by_type(commits: Iterator[Commit]):
    return groupby(
        sorted(commits, key=lambda x: TYPES_ORDERING.get(x.commit_type, 50)),
        attrgetter("commit_type"),
    )


class ChangelogGenerator:
    def __init__(self, parser: LogParser):
        self.parser = parser

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
        lines = list(self.parser.get_log(max_count=max_count, rev=rev, types=commit_types))
        if not lines:
            return ChangelogSection(version=from_version)
        commits, reverts, breaking_changes = tee(lines, 3)
        commits = filter(lambda line: line.revert is False, commits)
        reverts = list(filter(lambda line: line.revert is True, reverts))
        breaking_changes = list(filter(lambda line: line.breaking_change, breaking_changes))

        valid_types = [ct.name.lower() for ct in CommitType]

        section = ChangelogSection(
            version=from_version,
            changes={
                CommitType(commit_type): sorted(changes, key=lambda i: i.scope if i.scope else "")
                for commit_type, changes in group_commits_by_type(commits)
                if commit_type.lower() in valid_types
            },
            reverts=list(reverts),
            breaking_changes=(breaking_changes),
        )
        return section

    def get_changelog(
        self,
        commit_types: Optional[list[CommitType]] = None,
    ) -> Changelog:
        head = Version(name="HEAD", date=datetime.now(tz=TZ_INFO), semver=None)
        versions: list[Version] = [head, *self.parser.get_versions()]
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
