from mkchangelog.providers import GitLogProvider, LogProviderOptions


class TestGitLogProvider:
    def test_ignore_revs(self):
        ignored_revs = {
            "7cbb5e69b2984bc2c69434e49582bb84e2e31df6": "dev: Add flake.nix for `nix develop`\n",
            "947ff0d0149359150c07093cdda89fffc3592d72": "tests: fix ruff command used in github action\n",
        }

        # first, test plain log
        logs = GitLogProvider().get_log(LogProviderOptions(ignore_revs=None))
        for _, value in ignored_revs.items():
            assert value in logs

        # then, test with ignore_revs set
        logs = GitLogProvider().get_log(LogProviderOptions(ignore_revs=ignored_revs.keys()))
        for _, value in ignored_revs.items():
            assert value not in logs
