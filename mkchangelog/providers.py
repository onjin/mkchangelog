from __future__ import annotations

import abc
import glob
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from git import Repo

from mkchangelog.models import Version
from mkchangelog.utils import create_version


@dataclass
class LogProviderOptions:
    commit_limit: Optional[int] = 1000
    ignore_revs: Optional[List[str]] = None
    rev: Optional[str] = None
    types: Optional[list[str]] = None


class LogProvider(abc.ABC):
    @abc.abstractmethod
    def get_log(self, options: LogProviderOptions) -> Iterable[str]: ...


class VersionsProvider(abc.ABC):
    @abc.abstractmethod
    def get_versions(self, limit: Optional[int] = None) -> list[Version]: ...

    @abc.abstractmethod
    def get_last_version(self) -> Optional[Version]: ...


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
    def get_log(self, options: LogProviderOptions) -> Iterable[str]:
        """Return git log messages.

        Args:
            options: LogProviderOptions
        """
        repo = Repo(".")
        all_commits = repo.iter_commits(max_count=options.commit_limit, no_merges=True, rev=options.rev)

        if options.ignore_revs:
            all_commits = [c for c in all_commits if c.hexsha not in options.ignore_revs]
        return [c.message for c in all_commits]


class FilesLogProvider(LogProvider):
    """Returns commits messages from .mkchangelog.d/versions/vX.X.X/commits/ filders"""

    def get_log(self, options: LogProviderOptions) -> Iterable[str]:
        """Return git messages.

        Args:
            commit_limit (int, optional): max lines to parse
            rev (str, optional): git rev as branch name or range
        """
        messages: List[str] = []
        if options.rev:
            version = options.rev.split("...")[0]
            if version == "HEAD":
                version = "unreleased"
            path = Path(".") / ".mkchangelog.d" / "versions" / version / "commits"
        else:
            path = Path(".") / ".mkchangelog.d" / "versions" / "*" / "commits"
        files = glob.glob(str(path / "*.txt"))
        for file in files:
            with open(file, "r") as fh:
                messages.append(fh.read().strip("\n"))
        return messages
