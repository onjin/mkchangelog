from __future__ import annotations

from typing import Optional

from mkchangelog.config import Settings
from mkchangelog.core import ChangelogGenerator
from mkchangelog.models import CommitType, Version
from mkchangelog.parser import GitMessageParser
from mkchangelog.providers import GitLogProvider, GitVersionsProvider
from mkchangelog.renderers import RENDERERS, ChangelogRenderer


class Application:
    def __init__(self, *, settings: Settings, changelog_generator: ChangelogGenerator):
        self.settings = settings
        self.changelog_generator = changelog_generator

    def get_renderer(self, name: str, template: Optional[str] = None) -> ChangelogRenderer:
        try:
            renderer = RENDERERS[name]
            if renderer.__name__ == "TemplateChangelogRenderer" and template:
                return renderer(self.settings, template)
            return renderer(self.settings)
        except KeyError:
            return None

    def render_changelog(
        self, renderer: str, commit_types: Optional[list[CommitType]] = None, template: Optional[str] = None
    ):
        renderer = self.get_renderer(renderer, template)
        if not renderer:
            raise ValueError(f"Unknown renderer: {renderer}")

        return renderer.render(self.changelog_generator.get_changelog(commit_types=commit_types))

    def render_changelog_section(
        self,
        renderer: str,
        from_version: Optional[Version] = None,
        to_version: Optional[Version] = None,
        commit_types: Optional[list[CommitType, str]] = None,
    ):
        renderer = self.get_renderer(renderer)
        if not renderer:
            raise ValueError(f"Unknown renderer: {renderer}")
        return renderer.render_section(
            self.changelog_generator.get_changelog_section(
                from_version=from_version, to_version=to_version, commit_types=commit_types
            )
        )


def create_application(settings: Settings) -> Application:
    log_provider = GitLogProvider()
    versions_provider = GitVersionsProvider(tag_prefix=settings.git_tag_prefix)
    message_parser = GitMessageParser()
    changelog_generator = ChangelogGenerator(
        settings=settings, log_provider=log_provider, versions_provider=versions_provider, message_parser=message_parser
    )
    return Application(settings=settings, changelog_generator=changelog_generator)
