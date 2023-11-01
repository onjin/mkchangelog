from __future__ import annotations

import abc
import dataclasses
import json
from datetime import datetime
from typing import Any, Dict, List, Type

import semver

from mkchangelog.config import Settings
from mkchangelog.models import Changelog, ChangelogSection


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


class MarkdownChangelogRenderer(ChangelogRenderer):
    def render(self, changelog: Changelog) -> str:
        output = []
        output.append(f"# {self.settings.changelog_title}")
        output.append("")
        for section in changelog.sections:
            output.append(self.render_section(section))

        return "\n".join(output)

    def render_section(self, section: ChangelogSection) -> str:
        output: List[str] = []

        output.append(f"## {section.version.name} ({section.version.date})")
        output.append("")

        for commit_type in self.ordered_types(section.changes.keys()):
            changes = section.changes[commit_type]
            output.append(f"### {self.settings.commit_types.get(commit_type, commit_type.capitalize)}")
            output.append("")
            for row in changes:
                output.append(f"* {'**' + row.scope + ':**' if row.scope else ''}{row.summary}")
            output.append("")
        output.append("")

        return "\n".join(output)


class RstChangelogRenderer(ChangelogRenderer):
    def _header(self, name: str, level: str) -> str:
        return "\n".join([name, level * len(name)])

    def render(self, changelog: Changelog) -> str:
        output = []
        output.append(self._header(self.settings.changelog_title, "="))
        output.append("")
        for section in changelog.sections:
            output.append(self.render_section(section))

        return "\n".join(output)

    def render_section(self, section: ChangelogSection) -> str:
        output: List[str] = []

        output.append(self._header(f"{section.version.name} ({section.version.date})", "-"))
        output.append("")

        for commit_type in self.ordered_types(section.changes.keys()):
            changes = section.changes[commit_type]
            output.append(self._header(f"{self.settings.commit_types.get(commit_type, commit_type.capitalize)}", "^"))
            for row in changes:
                output.append(f"* {'**' + row.scope + ':**' if row.scope else ''}{row.summary}")
            output.append("")
        output.append("")

        return "\n".join(output)


RENDERERS: Dict[str, Type[ChangelogRenderer]] = {
    "json": JsonChangelogRenderer,
    "markdown": MarkdownChangelogRenderer,
    "rst": RstChangelogRenderer,
}
