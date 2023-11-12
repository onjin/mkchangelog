from __future__ import annotations

from mkchangelog.config import Settings, get_settings
from mkchangelog.models import Changelog, ChangelogSection, Version
from mkchangelog.parser import GitMessageParser
from mkchangelog.renderers import TextChangelogRenderer


class TestTextRenderer:
    def test_breaking_changes_presented(self):
        line = GitMessageParser(Settings()).parse(
            "feat(core)!: some important stuff here\n\nBREAKING CHANGE: bad news for compatibility"
        )
        changelog = Changelog(
            title="Changelog",
            sections=[
                ChangelogSection(
                    version=Version.from_str(name="v1.0.0", version="1.0.0"),
                    changes={"feat": [line]},
                    breaking_changes=[line],
                )
            ],
        )
        rendered = TextChangelogRenderer(get_settings()).render(changelog)

        assert "> ⚠ BREAKING CHANGES\n" in rendered
        assert "- bad news for compatibility\n" in rendered
