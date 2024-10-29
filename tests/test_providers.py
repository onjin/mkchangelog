from __future__ import annotations

from typing import Iterator

from git import Commit, Repo
from gitdb.db.loose import hex_to_bin

from mkchangelog.providers import GitLogProvider, LogProviderOptions


class FakeRepo(Repo):
    def iter_commits(self, *args, **kwargs) -> Iterator[Commit]:  # noqa:ARG002
        commits = {
            "6e8319de2a27501b9fec6c0d4de0c6f7888a2fb7": "docs(README.md): Add info about new `ignore_revs`",
            "7cbb5e69b2984bc2c69434e49582bb84e2e31df6": "dev: Add flake.nix for `nix develop`\n",
            "947ff0d0149359150c07093cdda89fffc3592d72": "tests: fix ruff command used in github action\n",
        }
        return [Commit(binsha=hex_to_bin(key), message=value, repo=Repo(".")) for key, value in commits.items()]


class FakeGitLogProvider(GitLogProvider):
    repo_factory = FakeRepo


class TestGitLogProvider:
    def test_ignore_revs(self) -> None:
        non_ignored_revs = {
            "6e8319de2a27501b9fec6c0d4de0c6f7888a2fb7": "docs(README.md): Add info about new `ignore_revs`",
        }
        ignored_revs = {
            "7cbb5e69b2984bc2c69434e49582bb84e2e31df6": "dev: Add flake.nix for `nix develop`\n",
            "947ff0d0149359150c07093cdda89fffc3592d72": "tests: fix ruff command used in github action\n",
        }

        # first, test plain log
        logs = FakeGitLogProvider().get_log(LogProviderOptions(ignore_revs=None))

        for value in non_ignored_revs.values():
            assert value in logs

        for value in ignored_revs.values():
            assert value in logs

        # then, test with ignore_revs set
        logs = FakeGitLogProvider().get_log(LogProviderOptions(ignore_revs=ignored_revs.keys()))

        for value in non_ignored_revs.values():
            assert value in logs

        for value in ignored_revs.values():
            assert value not in logs
