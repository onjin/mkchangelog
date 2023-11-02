from __future__ import annotations

from mkchangelog.config import get_settings
from mkchangelog.models import Changelog, ChangelogSection, Version
from mkchangelog.parser import GitMessageParser
from mkchangelog.renderers import TextChangelogRenderer


class TestTextRenderer:
    def test_breaking_changes_presented(self):
        changelog = Changelog(
            sections=[
                ChangelogSection(
                    version=Version.from_str(name="v1.0.0", version="1.0.0"),
                    changes={
                        "feat": [
                            GitMessageParser().parse(line)
                            for line in [
                                "feat(core)!: some important stuff here\n\nBREAKING CHANGE: bad news for compatibility"
                            ]
                        ]
                    },
                    breaking_changes=["bad news for compatibility"],
                )
            ]
        )
        rendered = TextChangelogRenderer(get_settings()).render(changelog)

        assert "> ⚠ BREAKING CHANGES\n" in rendered
        assert "- bad news for compatibility\n" in rendered
