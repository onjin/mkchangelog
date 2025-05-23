from __future__ import annotations

from collections import Counter
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterable

import semver

from mkchangelog.models import Changelog, ChangelogSection, CommitType, LogLine, Version
from mkchangelog.providers import LogProvider, LogProviderOptions, VersionsProvider
from mkchangelog.utils import TZ_INFO, create_version

if TYPE_CHECKING:
    from mkchangelog.config import Settings
    from mkchangelog.parser import GitMessageParser

DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


def get_next_version(tag_prefix: str, current_version: str, commits: list[LogLine]) -> Version | None:
    """
    Return next version or None if not available.

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
    elif "feat" in types:
        next_version = next_version.bump_minor()
    elif "fix" in types:
        next_version = next_version.bump_patch()

    # make next version
    if semver.VersionInfo.parse(current_version).compare(next_version) == 0:
        return None
    name = f"{tag_prefix}{next_version!s}"

    return Version(name=name, date=datetime.now(tz=TZ_INFO), semver=next_version)


class ChangelogGenerator:
    def __init__(
        self,
        settings: Settings,
        log_providers: list[LogProvider],
        versions_provider: VersionsProvider,
        message_parser: GitMessageParser,
        log_filters: list[Callable[[list[LogLine]], list[LogLine]]] | None = None,
    ) -> None:
        self.settings = settings
        self.log_providers = log_providers
        self.versions_provider = versions_provider
        self.message_parser = message_parser
        self.log_filters = log_filters

    def get_loglines(self, commits: list[str], *, strict: bool = False) -> list[LogLine]:
        lines: list[LogLine] = []
        for msg in commits:
            try:
                lines.append(self.message_parser.parse(msg))
            except ValueError:  # noqa: PERF203
                if strict:
                    raise
        if self.log_filters:
            for log_filter in self.log_filters:
                lines = log_filter(lines)
        return lines

    def group_commits_by_type(self, commits: Iterable[LogLine]) -> dict[str, Iterable[LogLine]]:
        grouped = {
            group: sorted(commits, key=lambda i: i.scope if i.scope else "")
            for group, commits in groupby(
                sorted(commits, key=lambda x: x.commit_type),
                attrgetter("commit_type"),
            )
        }
        # reorder groups to support types render priorities
        sorted_grouped: dict[str, list[LogLine]] = {}
        sorted_keys = sorted(
            grouped.keys(),
            key=lambda t: self.settings.commit_types_priorities.get(t, self.settings.commit_type_default_priority),
            reverse=True,
        )
        for key in sorted_keys:
            sorted_grouped[key] = grouped[key]

        return sorted_grouped

    def get_log_messages(self, commit_limit: int | None = None, rev: str | None = None) -> list[str]:
        msgs: list[str] = []
        for provider in self.log_providers:
            msgs.extend(
                provider.get_log(
                    LogProviderOptions(commit_limit=commit_limit, rev=rev, ignore_revs=self.settings.ignore_revs)
                )
            )
        return msgs

    def get_changelog_section(
        self,
        *,
        from_version: Version | None = None,
        to_version: Version | None = None,
        commit_types: list[CommitType] | None = None,
        commit_limit: int | None = None,
    ) -> ChangelogSection:
        if from_version is None:
            from_version = Version(name="HEAD", date=datetime.now(tz=TZ_INFO), semver=None)
        rev = from_version.name
        if to_version:
            rev = f"{rev}...{to_version.name}"
        messages = self.get_log_messages(commit_limit=commit_limit, rev=rev)
        log_lines: list[LogLine] = []
        log_lines = self.get_loglines(messages)

        # filter by commit_types
        breaking_changes = [line for line in log_lines if line.breaking_change is True]
        if commit_types:
            log_lines = [line for line in log_lines if line.commit_type in commit_types or "all" in commit_types]
        reverts = [line for line in log_lines if line.commit_type == "revert"]

        header = ""
        header_path = Path(".mkchangelog.d", "versions", from_version.name, "header")
        footer = ""
        footer_path = Path(".mkchangelog.d", "versions", from_version.name, "footer")
        if header_path.exists():
            with open(header_path) as fh:
                header = fh.read().strip()

        if footer_path.exists():
            with open(footer_path) as fh:
                footer = fh.read().strip()
        if not log_lines:
            return ChangelogSection(version=from_version, header=header, footer=footer)

        def type_name(commit_type: str) -> str:
            return self.settings.commit_types.get(commit_type, commit_type.capitalize())

        return ChangelogSection(
            version=from_version,
            changes={
                type_name(commit_type): changes
                for commit_type, changes in self.group_commits_by_type(log_lines).items()
            },
            reverts=reverts,
            breaking_changes=breaking_changes,
            header=header,
            footer=footer,
        )

    def get_changelog(
        self,
        *,
        title: str | None = None,
        commit_types: list[CommitType] | None = None,
        unreleased: bool = False,
        unreleased_version: str = "Unreleased",
        hide_empty_releases: bool = False,
        commit_limit: int | None = None,
    ) -> Changelog:
        if title is None:
            title = self.settings.changelog_title
        versions: list[Version] = []
        if unreleased:
            head = Version(name="HEAD", date=datetime.now(tz=TZ_INFO), semver=None)
            versions.append(head)
        versions.extend(self.versions_provider.get_versions())
        if not versions:
            return Changelog(title=title, sections=[])
        if len(versions) == 1:
            # just head -> all
            return Changelog(
                title=title,
                sections=[self.get_changelog_section(from_version=versions[0], commit_types=commit_types)],
            )

        sections: list[ChangelogSection] = []
        while len(versions) > 1:
            sections.append(
                self.get_changelog_section(
                    from_version=versions[0],
                    to_version=versions[1],
                    commit_types=commit_types,
                    commit_limit=commit_limit,
                )
            )
            versions = versions[1:]
        sections.append(
            self.get_changelog_section(from_version=versions[0], commit_types=commit_types, commit_limit=commit_limit)
        )

        for section in sections:
            if section.version.name == "HEAD":
                section.version.name = unreleased_version
        if hide_empty_releases:
            sections = [section for section in sections if section.changes]
        return Changelog(title=title, sections=sections)
