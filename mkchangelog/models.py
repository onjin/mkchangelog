from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from git import Commit


class CommitType(str, Enum):
    BUILD = "build"
    CHORE = "chore"
    CI = "ci"
    DEV = "dev"
    DOCS = "docs"
    FEAT = "feat"
    FIX = "fix"
    PERF = "perf"
    REFACTOR = "refactor"
    STYLE = "style"
    TEST = "text"
    TRANSLATIONS = "translations"


TYPES: Dict[CommitType, str] = {
    CommitType.BUILD: "Build",
    CommitType.CHORE: "Chore",
    CommitType.CI: "CI",
    CommitType.DEV: "Dev",
    CommitType.DOCS: "Docs",
    CommitType.FEAT: "Features",
    CommitType.FIX: "Fixes",
    CommitType.PERF: "Performance",
    CommitType.REFACTOR: "Refactors",
    CommitType.STYLE: "Style",
    CommitType.TEST: "Test",
    CommitType.TRANSLATIONS: "Translations",
}

# default priority is 10 so we need only
TYPES_ORDERING: Dict[CommitType, int] = {
    CommitType.FEAT: 10,
    CommitType.FIX: 20,
    CommitType.REFACTOR: 30,
}


@dataclass(frozen=True)
class LogLine:
    message: str
    commit_type: str
    title: str
    scope: str = ""
    revert: bool = False
    references: list[str] = field(default_factory=list)
    breaking_change: str = ""
    subject: str = ""


@dataclass(frozen=True)
class MatchedLine:
    log: Commit
    groups: Dict[str, Any]


@dataclass(frozen=True)
class Version:
    name: str
    date: datetime
    semver: str


@dataclass
class ChangelogSection:
    version: Optional[Version]
    changes: Dict[CommitType, List[LogLine]] = field(default_factory=dict)
    reverts: List[LogLine] = field(default_factory=list)
    breaking_changes: List[LogLine] = field(default_factory=list)


@dataclass
class Changelog:
    sections: List[ChangelogSection]
