from __future__ import annotations

import abc
from typing import Generator, Optional

from git import Repo

from mkchangelog.models import LogLine, Version
from mkchangelog.utils import create_version


class LogProvider(abc.ABC):
    @abc.abstractmethod
    def get_log(self, max_count: int = 1000, rev: Optional[str] = None) -> Generator[LogLine, None, None]:
        ...


class VersionsProvider(abc.ABC):
    @abc.abstractmethod
    def get_versions(self, limit: Optional[int] = None) -> list[Version]:
        ...

    @abc.abstractmethod
    def get_last_version(self) -> Optional[Version]:
        ...


class GitVersionsProvider(VersionsProvider):
    TAG_PREFIX = "v"

    def __init__(self, tag_prefix: str = TAG_PREFIX):
        self._tag_prefix = tag_prefix

    def get_versions(self, limit: Optional[int] = None) -> list[Version]:
        """Return versions lists

        Args:
            limit (int) - limit versions returned

        Returns:
            list(Version(name, date))
        """
        repo = Repo(".")
        versions = [
            Version(
                name=tag.name,
                date=tag.commit.authored_datetime,
                semver=create_version(self._tag_prefix, tag.name),
            )
            for tag in repo.tags
            if tag.name.startswith(self._tag_prefix)
        ]
        sorted_versions = sorted(versions, key=lambda v: v.date, reverse=True)
        if limit:
            return sorted_versions[:limit]
        return sorted_versions

    def get_last_version(self) -> Optional[Version]:
        """Return last bumped version

        Returns:
            Version(name, date)
        """
        versions = self.get_versions(limit=1)
        if versions:
            return versions[0]
        return None


class GitLogProvider(LogProvider):
    def get_log(self, max_count: int = 1000, rev: Optional[str] = None) -> Generator[LogLine, None, None]:
        """Return git log parsed using Conventional Commit format.

        Args:
            max_count (int, optional): max lines to parse
            rev (str, optional): git rev as branch name or range
        """
        repo = Repo(".")
        return [commit.message for commit in repo.iter_commits(max_count=max_count, no_merges=True, rev=rev)]
