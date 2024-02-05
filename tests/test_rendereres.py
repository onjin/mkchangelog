from __future__ import annotations

import pytest

from mkchangelog.config import Settings, get_settings
from mkchangelog.lib import regex_replace_filter
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


@pytest.mark.parametrize(
    "value,pattern,replacement,ignorecase,multiline,expected",
    (
        ("line with #12 issue ref", r"#(\d+)", "#ISSUE-\\1", False, False, "line with #ISSUE-12 issue ref"),
        ("localhost:80", "^(?P<host>.+):(?P<port>\\d+)$", "\\g<host>, \\g<port>", False, False, "localhost, 80"),
        ("some CASE1 test", r"[a-z]", "x", False, False, "xxxx CASE1 xxxx"),
        ("some CASE2 test", r"[a-z]", "x", True, False, "xxxx xxxx2 xxxx"),
    ),
)
def test_regex_replace_filter(  # noqa: #FBT001
    value: str,
    pattern: str,
    replacement: str,
    ignorecase: bool,  # noqa: FBT001
    multiline: bool,  # noqa: FBT001
    expected: str,
):
    assert regex_replace_filter(value, pattern, replacement, ignorecase, multiline) == expected
