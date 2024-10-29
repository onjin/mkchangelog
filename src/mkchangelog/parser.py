from __future__ import annotations

import re
import textwrap
from collections import defaultdict
from typing import Any, Dict, Match, Optional

from mkchangelog.config import Settings
from mkchangelog.models import LogLine


class GitMessageParser:
    # https://regex101.com/r/zxMWuT/1

    CC_REGEXP = re.compile(
        r"^(?P<revert>revert: |Revert \")?(?P<type>[a-z0-9]+)(?P<scope>\([a-zA-Z0-9\._-]+\))?: (?P<title>.*)$"
    )

    REF_REGEXP = re.compile(
        r"^\s*(?P<action>[\w -]+): (?P<refs>.*)$",
        re.MULTILINE,
    )

    # Regex for BREAKING CHANGE section
    BREAKING_CHANGES_REGEXP = re.compile(
        r"(?s)BREAKING CHANGE:(?P<breaking_change>.*?)(?:(?:\r*\n){2})",
        re.MULTILINE,
    )

    # Regex for Requires trailer for manual actions requiremenets
    REQ_REGEXP = re.compile(
        r"(?s)Requires:(?P<requires>.*?)(?:(?:\r*\n){2})",
        re.MULTILINE,
    )

    def __init__(self, settings: Settings):
        types = "|".join(settings.commit_types.keys())
        self.COMMIT_REGEXP = re.compile(
            (
                r"(?P<initial_commit>^Initial commit\.?)"
                r"|(?P<merge>^Merge [^\r\n]+)"
                rf"|(?P<type>^{types}|¯\\_\\(ツ\\)_\\/¯)"
                r"(?:\((?P<scope>[\w\.-]+)\))?"
                r"(?P<breaking>!)?"
                r": "
                r"(?P<summary>.+)$"
            ),
            re.MULTILINE,
        )
        self.REF_ALIASES = settings.reference_aliases

    def _get_references_from_msg(self, msg: str) -> dict[str, set[str]]:
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
        result = self.REF_REGEXP.findall(msg)
        if not result:
            return None

        refs: dict[str, set[str]] = defaultdict(set)
        for line in result:
            action, value = line
            for main, aliases in self.REF_ALIASES.items():
                if action in aliases:
                    action = main
            for ref in value.split(","):
                refs[action].add(ref.strip())
        return dict(refs)

    def _get_breaking_changes(self, message: str) -> Optional[list[str]]:
        """Returns list of breaking changes descriptions

        Example message:
            feat(admin): asdfasdfsdf

            some body

            BREAKING CHANGE:
                someone
                broken
                here

        Returns:
            list - ['someone\nbroken\nhere']
        """
        breaking_changes = self.BREAKING_CHANGES_REGEXP.findall(message)
        if not breaking_changes:
            return None
        return [textwrap.dedent(change.strip("\n")) for change in breaking_changes]

    def parse(self, message: str) -> LogLine:
        message = message.strip()
        if "\n" in message:
            first_line, body = message.split("\n", 1)
        else:
            first_line, body = message, ""
        match: Optional[Match[Dict[str, Any]]] = self.COMMIT_REGEXP.search(first_line)
        if not match:
            raise ValueError(f"Invalid commit {first_line}")
        parts: Dict[str, Any] = match.groupdict()
        references = self._get_references_from_msg(body) or {}
        breaking_changes = references.get("BREAKING CHANGE", set())
        breaking_change = bool(breaking_changes or parts["breaking"] == "!")
        return LogLine(
            message=message,
            commit_type=parts["type"],
            scope=parts["scope"],
            summary=parts["summary"],
            references=references,
            breaking_change=breaking_change,
            breaking_changes=breaking_changes,
        )
