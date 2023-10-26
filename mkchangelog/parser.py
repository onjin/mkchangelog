from __future__ import annotations

import abc
import re
from collections import defaultdict
from typing import Generator, Iterator, Optional

from git import Commit, Repo

from mkchangelog.models import LogLine, MatchedLine, Version
from mkchangelog.utils import create_version

REFERENCE_ACTIONS = ["Closes", "Relates"]


class LogParser(abc.ABC):
    @abc.abstractmethod
    def get_versions(self, tag_prefix: str, limit: Optional[int] = None) -> list[Version]:
        ...

    @abc.abstractmethod
    def get_last_version(self, tag_prefix: str) -> Optional[Version]:
        ...

    @abc.abstractmethod
    def get_log(
        self, max_count: int = 1000, rev: Optional[str] = None, types: Optional[list[str]] = None
    ) -> Generator[LogLine, None, None]:
        ...


class GitLogParser(LogParser):
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

    def get_versions(self, tag_prefix: str, limit: Optional[int] = None) -> list[Version]:
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
                semver=create_version(tag_prefix, tag.name),
            )
            for tag in repo.tags
            if tag.name.startswith(tag_prefix)
        ]
        sorted_versions = sorted(versions, key=lambda v: v.date, reverse=True)
        if limit:
            return sorted_versions[:limit]
        return sorted_versions

    def get_last_version(self, tag_prefix: str) -> Optional[Version]:
        """Return last bumped version

        Args:
            tag_prefix (str): version tags prefix

        Returns:
            Version(name, date)
        """
        versions = self.get_versions(tag_prefix=tag_prefix, limit=1)
        if versions:
            return versions[0]
        return None

    def _get_references_from_msg(self, msg: bytes) -> dict[str, set[str]]:
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
        result = self.REF_REGEXP.findall(msg.decode("utf-8"))
        if not result:
            return None

        refs: dict[str, set[str]] = defaultdict(set)
        for line in result:
            action, value = line
            for ref in value.split(","):
                refs[action].add(ref.strip())
        return refs

    def _get_lines_from_commits(self, commits: Iterator[Commit]) -> Generator[MatchedLine, None, None]:
        return (
            MatchedLine(c, self.CC_REGEXP.match(c.summary).groupdict())
            for c in commits
            if self.CC_REGEXP.match(c.summary)
        )

    def get_log(
        self, max_count: int = 1000, rev: Optional[str] = None, types: Optional[list[str]] = None
    ) -> Generator[LogLine, None, None]:
        """Return git log parsed using Conventional Commit format.

        Args:
            max_count (int, optional): max lines to parse
            rev (str, optional): git rev as branch name or range
        """
        repo = Repo(".")
        commits = repo.iter_commits(max_count=max_count, no_merges=True, rev=rev)
        cc_commits = self._get_lines_from_commits(commits)
        messages = (
            LogLine(
                subject=line.log.summary.encode(line.log.encoding),
                message=line.log.message.encode(line.log.encoding),
                revert=True if line.groups["revert"] else False,
                commit_type=line.groups["type"],
                scope=line.groups["scope"][1:-1] if line.groups["scope"] else line.groups["scope"],
                title=line.groups["title"],
                references=self._get_references_from_msg(line.log.message.encode(line.log.encoding)),
                breaking_change=(self.BC_REGEXP.findall(line.log.message) or [None])[0],
            )
            for line in cc_commits
        )
        if types:
            messages = (line for line in messages if line.commit_type in types)
        return messages


__all__ = ["GitLogParser"]
