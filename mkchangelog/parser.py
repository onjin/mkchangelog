from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from typing import Any, Dict, Iterator, Optional

import semver
from git import Commit, Repo

from mkchangelog.base import TZ_INFO

REFERENCE_ACTIONS = ["Closes", "Relates"]

TYPES = {
    "build": "Build",
    "chore": "Chore",
    "ci": "CI",
    "dev": "Dev",
    "docs": "Docs",
    "feat": "Features",
    "fix": "Fixes",
    "perf": "Performance",
    "refactor": "Refactors",
    "style": "Style",
    "test": "Test",
    "translations": "Translations",
}
# default priority is 10 so we need only
ORDERING = {
    "feat": 10,
    "fix": 20,
    "refactor": 30,
}

REF_REGEXP = re.compile(
    r"^\s+?(?P<action>{actions})\s+(?P<refs>.*)$".format(actions="|".join(REFERENCE_ACTIONS)),
    re.MULTILINE,
)
# Regexp for commit subject
CC_REGEXP = re.compile(r"^(?P<revert>revert: |Revert \")?(?P<type>[a-z0-9]+)(?P<scope>\([ \w]+\))?: (?P<title>.*)$")

# Regex for BREAKING CHANGE section
BC_REGEXP = re.compile(
    r"(?s)BREAKING CHANGE:(?P<breaking_change>.*?)(?:(?:\r*\n){2})",
    re.MULTILINE,
)

# Regex for Requires trailer for manual actions requiremenets
REQ_REGEXP = re.compile(
    r"(?s)Requires:(?P<requires>.*?)(?:(?:\r*\n){2})",
    re.MULTILINE,
)


@dataclass(frozen=True)
class LogLine:
    subject: str
    message: str
    revert: bool
    commit_type: str
    scope: str
    title: str
    references: list[str]
    breaking_change: str


@dataclass(frozen=True)
class MatchedLine:
    log: Commit
    groups: Dict[str, Any]


@dataclass(frozen=True)
class Version:
    name: str
    date: datetime
    semver: str


def group_commits_by_type(commits: Iterator[Commit]):
    return groupby(
        sorted(commits, key=lambda x: ORDERING.get(x.commit_type, 50)),
        attrgetter("commit_type"),
    )


def get_references_from_msg(msg: bytes) -> dict[str, set[str]]:
    """Get references from commit message

    Args:
        msg (str): commit message


    Returns:
        dict[set] - dictionary with references

        example:
            {
                "Closes": set("ISS-123", "ISS-321")
            }
    """
    result = REF_REGEXP.findall(msg.decode("utf-8"))
    if not result:
        return None

    refs: dict[str, set[str]] = defaultdict(set)
    for line in result:
        action, value = line
        for ref in value.split(","):
            refs[action].add(ref.strip())
    return refs


def v2s(prefix: str, version: str) -> semver.Version:
    """Convert version name to semantic version

    Args:
        prefix (str): version tags prefix
        version (str): version name to convert

    Returns:
        semver.Semver - semantic version object
    """
    return semver.Version.parse(version[len(prefix) :])


def get_git_versions(tag_prefix: str) -> list[semver.Version]:
    """Return versions lists

    Args:
        tag_prefix (str): versions tags prefix

    Returns:
        list(Version(name, date))
    """
    repo = Repo(".")
    versions = [
        Version(
            name=tag.name,
            date=tag.commit.authored_datetime,
            semver=v2s(tag_prefix, tag.name),
        )
        for tag in repo.tags
        if tag.name.startswith(tag_prefix)
    ]
    return sorted(versions, key=lambda v: v.date, reverse=True)


def get_last_version(tag_prefix: str) -> Optional[Version]:
    """Return last bumped bersion

    Args:
        tag_prefix (str): version tags prefix

    Returns:
        Version(name, date)
    """
    versions = get_git_versions(tag_prefix=tag_prefix)
    if not len(versions):
        return None
    return versions[0]


def get_next_version(tag_prefix: str, current_version: str, commits: list[LogLine]) -> Optional[Version]:
    """Return next version or None if not available

    Args:
        tag_prefix (str): version tags prefix
        current_version (str): current version, f.i. v1.1.1
        commits (list): list of LogLine containing commits till current version

    Returns:
        Version | None - next version object or None if no new version is available.
    """
    next_version = v2s(tag_prefix, current_version)
    current_version = str(next_version)

    # count types {{{
    types: dict[str, int] = Counter()
    for commit in commits:
        types[commit.commit_type] += 1
        if commit.breaking_change:
            types["breaking_change"] += 1
    # count types }}}

    # bump version {{{
    breaking_change: int = types.get("breaking_change", 0)
    if breaking_change > 0:
        next_version = next_version.bump_major()
    elif "feat" in types.keys():
        next_version = next_version.bump_minor()
    elif "fix" in types.keys():
        next_version = next_version.bump_patch()
    # bump version }}}

    # make next version {{{
    if semver.compare(current_version, str(next_version)) == 0:
        return None
    name = f"{tag_prefix}{next_version!s}"
    return Version(name=name, date=datetime.now(tz=TZ_INFO), semver=next_version)


def get_git_log(max_count: int = 1000, rev: Optional[str] = None, types: Optional[list[str]] = None):
    """Return git log parsed using Conventional Commit format.

    Args:
        max_count (int, optional): max lines to parse
        rev (str, optional): git rev as branch name or range
    """
    repo = Repo(".")
    commits = repo.iter_commits(max_count=max_count, no_merges=True, rev=rev)
    cc_commits = (MatchedLine(c, CC_REGEXP.match(c.summary).groupdict()) for c in commits if CC_REGEXP.match(c.summary))
    messages = (
        LogLine(
            subject=line.log.summary.encode(line.log.encoding),
            message=line.log.message.encode(line.log.encoding),
            revert=True if line.groups["revert"] else False,
            commit_type=line.groups["type"],
            scope=line.groups["scope"][1:-1] if line.groups["scope"] else line.groups["scope"],
            title=line.groups["title"],
            references=get_references_from_msg(line.log.message.encode(line.log.encoding)),
            breaking_change=(BC_REGEXP.findall(line.log.message) or [None])[0],
        )
        for line in cc_commits
    )
    if types and "all" not in types:
        log_types = types
    else:
        log_types = TYPES.keys()
    messages = (line for line in messages if line.commit_type in log_types)
    return messages
