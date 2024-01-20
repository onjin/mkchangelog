from __future__ import annotations

import textwrap
from inspect import isclass
from typing import Union

import pytest

from mkchangelog.config import Settings
from mkchangelog.parser import GitMessageParser


class TestRegexpes:
    @pytest.mark.parametrize(
        "message,matches",
        [
            (
                "super feature landed",
                ValueError,
            ),
            (
                "feat: super feature landed",
                {"commit_type": "feat", "scope": None, "summary": "super feature landed"},
            ),
            (
                "feat(admin): super feature landed",
                {"commit_type": "feat", "scope": "admin", "summary": "super feature landed"},
            ),
            (
                "feat(admin): super feature landed\n\nonly body here",
                {
                    "commit_type": "feat",
                    "scope": "admin",
                    "breaking_change": False,
                    "summary": "super feature landed",
                },
            ),
            (
                "feat(admin): super feature landed\n\nonly footer: here",
                {
                    "commit_type": "feat",
                    "scope": "admin",
                    "summary": "super feature landed",
                },
            ),
            (
                "fix(some)!: prevent racing of requests",
                {
                    "commit_type": "fix",
                    "scope": "some",
                    "breaking_change": True,
                    "summary": "prevent racing of requests",
                },
            ),
            (
                "fix(parser): stranger chars: `x-explain: 1` `or_=` queries",
                {"commit_type": "fix", "scope": "parser", "summary": "stranger chars: `x-explain: 1` `or_=` queries"},
            ),
        ],
    )
    def test_commit_regexp(self, message: str, matches: Union[dict[str, str], Exception]):
        # When - matched against summary regexp
        if isclass(matches) and issubclass(matches, Exception):
            with pytest.raises(matches):
                result = GitMessageParser(Settings()).parse(message)
        else:
            result = GitMessageParser(Settings()).parse(message)
            # Then - commit is parsed properly
            for key in matches.keys():
                assert getattr(result, key) == matches[key], result


class TestGitLogParser:
    def test_commit_subject_regexp(self):
        # Given -  feature with scope
        message = "feat(admin): super feature landed"

        # When - matched against summary regexp
        line = GitMessageParser(Settings()).parse(message)

        # Then - commit is parsed properly
        assert line.commit_type == "feat"
        assert line.scope == "admin"
        assert line.summary == "super feature landed"

    def test_body_and_footer_references_regexp(self):
        # Given - msg with body and footer
        message = textwrap.dedent(
            """feat(admin): asdfasdfsdf

        body someid

        Closes: ISS-123, ISS-432
        Relates: ISS-223, ISS-232
        """
        )
        # When - matched against full commit regexp
        line = GitMessageParser(Settings()).parse(message)

        # Then - we got all footer references
        assert line.references == {
            "Closes": {"ISS-123", "ISS-432"},
            "Relates": {"ISS-223", "ISS-232"},
        }

    def test_only_footer_references_regexp(self):
        # Given - msg with no body and footer
        message = """feat(admin): asdfasdfsdf

        Closes: ISS-123, ISS-432
        Relates: ISS-223, ISS-232
        """
        # When - matched against full commit regexp
        line = GitMessageParser(Settings()).parse(message)

        # Then - we got all footer references
        assert line.references == {
            "Closes": {"ISS-123", "ISS-432"},
            "Relates": {"ISS-223", "ISS-232"},
        }

    def test_get_references_from_msg(self):
        # Given - msg with references
        message = """feat(admin): asdfasdfsdf

        Closes: C-001, C-002
        Close: C-003,C-004
        Closed: C-005,C-006
        Fixes: F-001, F-002
        Fix: F-003,F-004
        Fixed: F-005,F-006
        Resolves: RS-001, RS-002
        Resolve: RS-003,RS-004
        Resolved: RS-005,RS-006, RS-007
        Relates: R-001, R-002
        Relate: R-003,R-004
        Related: R-005,R-006, R-007
        """

        # When - we get parsed references
        line = GitMessageParser(Settings()).parse(message)

        # Then - we get dict with actions as keys and refs as values list
        assert line.references is not None
        assert set(line.references.keys()) == {"Closes", "Relates", "Fixes", "Resolves"}
        assert sorted(line.references["Closes"]) == [
            "C-001",
            "C-002",
            "C-003",
            "C-004",
            "C-005",
            "C-006",
        ]
        assert sorted(line.references["Relates"]) == [
            "R-001",
            "R-002",
            "R-003",
            "R-004",
            "R-005",
            "R-006",
            "R-007",
        ]
        assert sorted(line.references["Fixes"]) == [
            "F-001",
            "F-002",
            "F-003",
            "F-004",
            "F-005",
            "F-006",
        ]
        assert sorted(line.references["Resolves"]) == [
            "RS-001",
            "RS-002",
            "RS-003",
            "RS-004",
            "RS-005",
            "RS-006",
            "RS-007",
        ]

    @pytest.mark.parametrize(
        "message,changes",
        [
            (
                textwrap.dedent(
                    """
        feat(admin): asdfasdfsdf

        some body

        BREAKING CHANGE: someone broke smth
        Closes: ISS-123, ISS-432
        Relates: ISS-223, ISS-232
        """
                ),
                {"someone broke smth"},
            ),
            (
                textwrap.dedent(
                    """
        feat(api): some

        body

        BREAKING CHANGE: API broken badly
        """
                ),
                {"API broken badly"},
            ),
        ],
    )
    def test_gather_breaking_changes(self, message: str, changes: list[str]):
        # Given - breaking changes in footer
        # When - matched against regexp
        line = GitMessageParser(Settings()).parse(message)

        # Then - we got all rows
        assert line.breaking_changes == changes
