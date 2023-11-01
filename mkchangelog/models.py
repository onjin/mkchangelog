from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, NewType, Optional, Set

from git import Commit

if TYPE_CHECKING:
    pass

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
    scope: Optional[str] = None

    # parsed referenced tickets
    references: Optional[Dict[str, Set[str]]] = None

    # parsed BREAKING CHANGE: paragraph
    breaking_change: bool = False
    breaking_changes: Optional[Dict[str, str]] = None

    # TODO: change core code to put original commit here
    commit: Optional[Commit] = None


@dataclass(frozen=True)
class MatchedLine:
    message: str
    summary: str
    groups: Dict[str, Any]


@dataclass(frozen=True)
class Version:
    name: str
    date: Optional[datetime] = None
    semver: Optional[str] = None


@dataclass
class ChangelogSection:
    version: Optional[Version]
    changes: Dict[CommitType, List[LogLine]] = field(default_factory=dict)
    reverts: List[LogLine] = field(default_factory=list)
    breaking_changes: List[LogLine] = field(default_factory=list)


@dataclass
class Changelog:
    sections: List[ChangelogSection]
