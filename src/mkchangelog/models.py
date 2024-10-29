from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, NewType

import semver

from mkchangelog.utils import TZ_INFO

if TYPE_CHECKING:
    from git import Commit

CommitType = NewType("CommitType", str)


@dataclass(frozen=True)
class LogLine:
    # whole git message
    message: str

    # first line of commit `message`
    summary: str

    # parsed commit type, f.e.: feat, fix
    commit_type: str

    # optional parsed scope from
    scope: str | None = None

    # parsed referenced tickets
    references: dict[str, set[str]] | None = None

    # parsed BREAKING CHANGE: paragraph
    breaking_change: bool = False
    breaking_changes: dict[str, str] | None = None

    commit: Commit | None = None


@dataclass(frozen=True)
class MatchedLine:
    message: str
    summary: str
    groups: dict[str, Any]


@dataclass()
class Version:
    name: str
    date: datetime | None = None
    semver: str | None = None

    @classmethod
    def from_str(cls, name: str, version: str) -> Version:
        semver_version = semver.Version.parse(version)
        return cls(name, datetime.now(tz=TZ_INFO), semver_version)


@dataclass
class ChangelogSection:
    version: Version | None
    changes: dict[CommitType, list[LogLine]] = field(default_factory=dict)
    reverts: list[LogLine] = field(default_factory=list)
    breaking_changes: list[LogLine] = field(default_factory=list)
    header: str = ""
    footer: str = ""


@dataclass
class Changelog:
    title: str
    sections: list[ChangelogSection]
