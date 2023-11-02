from __future__ import annotations

import abc
import dataclasses
import json
from datetime import datetime
from typing import Any, Dict, List, Type

import semver

from mkchangelog.config import Settings
from mkchangelog.models import Changelog, ChangelogSection, LogLine


class ChangelogRenderer(abc.ABC):
    def __init__(self, settings: Settings):
        self.settings = settings

    @abc.abstractmethod
    def render(self, changelog: Changelog) -> Any:
        ...

    @abc.abstractmethod
    def render_section(self, section: ChangelogSection) -> Any:
        ...

    def ordered_types(self, types: List[str]) -> List[str]:
        """Return commit types sorted by ordering priority."""
        return sorted(
            types,
            key=lambda t: self.settings.commit_types_priorities.get(t, self.settings.commit_type_default_priority),
            reverse=True,
        )


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, semver.Version):
            return str(o)

        return super().default(o)


class JsonChangelogRenderer(ChangelogRenderer):
    def dumps(self, obj: Any):
        return json.dumps(obj, cls=EnhancedJSONEncoder)

    def render(self, changelog: Changelog) -> Any:
        return self.dumps(changelog)

    def render_section(self, section: ChangelogSection) -> Any:
        return self.dumps(section)


class TextChangelogRenderer(ChangelogRenderer):
    def _header(self, name: str, level: int) -> str:
        if level == 1:
            return f".-= {name} =-."
        elif level == 2:  # noqa: PLR2004
            return name
        else:
            return f"> {name}"

    def _list_item(self, line: LogLine) -> str:
        return f"- {'**' + line.scope + ':**' if line.scope else ''}{line.summary}"

    def _break(self) -> str:
        return ""

    def render(self, changelog: Changelog) -> str:
        output: List[str] = []
        output.append(self._header(self.settings.changelog_title, 1))
        output.append(self._break())
        for section in changelog.sections:
            if not section.changes and section.version and section.version.name == "HEAD":
                continue
            output.append(self.render_section(section))
        return "\n".join(output)

    def render_section(self, section: ChangelogSection) -> str:
        output: List[str] = []

        output.append(self._header(f"{section.version.name} ({section.version.date})", level=2))
        output.append(self._break())

        for commit_type in self.ordered_types(section.changes.keys()):
            changes = section.changes[commit_type]
            output.append(self._header(self.settings.commit_types.get(commit_type, commit_type.capitalize), level=3))
            output.append(self._break())
            for row in changes:
                output.append(self._list_item(row))
            output.append(self._break())

        return "\n".join(output)


class MarkdownChangelogRenderer(TextChangelogRenderer):
    def _header(self, name: str, level: int) -> str:
        return f"{'#' * level} {name}"

    def _list_item(self, line: LogLine) -> str:
        return f"* {'**' + line.scope + ':**' if line.scope else ''}{line.summary}"


class RstChangelogRenderer(TextChangelogRenderer):
    def _header(self, name: str, level: int) -> str:
        mark = {1: "=", 2: "-", 3: "^"}
        return "\n".join([name, mark.get(level, "^") * len(name)])

    def _list_item(self, line: LogLine) -> str:
        return f"* {'**' + line.scope + ':**' if line.scope else ''}{line.summary}"


RENDERERS: Dict[str, Type[ChangelogRenderer]] = {
    "json": JsonChangelogRenderer,
    "markdown": MarkdownChangelogRenderer,
    "rst": RstChangelogRenderer,
    "txt": TextChangelogRenderer,
}
