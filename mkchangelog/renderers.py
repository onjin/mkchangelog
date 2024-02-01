from __future__ import annotations

import abc
import dataclasses
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Type

import semver
from git import Optional
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape

from mkchangelog.config import Settings
from mkchangelog.models import Changelog, ChangelogSection


class BaseChangelogRenderer:
    def ordered_types(self, types: List[str]) -> List[str]:
        """Return commit types sorted by ordering priority."""
        return sorted(
            types,
            key=lambda t: self.settings.commit_types_priorities.get(t, self.settings.commit_type_default_priority),
            reverse=True,
        )


class TemplateChangelogRenderer(BaseChangelogRenderer, abc.ABC):
    TEMPLATE: str = None

    def __init__(self, settings: Settings, template: Optional[str] = None):
        self.settings = settings

        # support absolute templates path
        if template and template.startswith("/"):
            template = template[1:]

        self.template = template or self.TEMPLATE
        if template:
            loader = FileSystemLoader([Path.cwd(), Path.cwd().root], followlinks=True)
        else:
            loader = PackageLoader("mkchangelog")

        self.env = Environment(loader=loader, autoescape=select_autoescape(), trim_blocks=True, lstrip_blocks=True)
        self.env.filters["underline"] = lambda line, char: f"{line}\n{ char * len(line)}"

    def render(self, changelog: Changelog) -> Any:
        template = self.env.get_template(self.template)
        ctx = {
            "settings": self.settings,
            "changelog": changelog,
        }
        return template.render(**ctx)


class ChangelogRenderer(BaseChangelogRenderer, abc.ABC):
    def __init__(self, settings: Settings):
        self.settings = settings

    @abc.abstractmethod
    def render(self, changelog: Changelog) -> Any: ...

    @abc.abstractmethod
    def render_section(self, section: ChangelogSection) -> Any: ...


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


class TextChangelogRenderer(TemplateChangelogRenderer):
    TEMPLATE = "text.jinja2"


class MarkdownChangelogRenderer(TemplateChangelogRenderer):
    TEMPLATE = "markdown.jinja2"


class RstChangelogRenderer(TemplateChangelogRenderer):
    TEMPLATE = "rst.jinja2"


RENDERERS: Dict[str, Type[ChangelogRenderer]] = {
    "json": JsonChangelogRenderer,
    "markdown": MarkdownChangelogRenderer,
    "rst": RstChangelogRenderer,
    "txt": TextChangelogRenderer,
}
