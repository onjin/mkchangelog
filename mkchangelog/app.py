from __future__ import annotations

from typing import Optional

from mkchangelog.config import Settings
from mkchangelog.core import ChangelogGenerator
from mkchangelog.models import CommitType, Version
from mkchangelog.parser import GitMessageParser
from mkchangelog.providers import FilesLogProvider, GitLogProvider, GitVersionsProvider
from mkchangelog.renderers import RENDERERS, ChangelogRenderer, TemplateChangelogRenderer


class Application:
    def __init__(self, *, settings: Settings, changelog_generator: ChangelogGenerator):
        self.settings = settings
        self.changelog_generator = changelog_generator

    def get_renderer(self, name: str) -> ChangelogRenderer:
        try:
            renderer = RENDERERS[name]
            return renderer(self.settings)
        except KeyError:
            return TemplateChangelogRenderer(self.settings, name)

    def render_changelog(
        self,
        *,
        template: Optional[str] = None,
        title: Optional[str] = None,
        commit_types: Optional[list[CommitType]] = None,
        unreleased: bool = False,
        unreleased_version: str = "Unreleased",
        hide_empty_releases: bool = False,
        commit_limit: Optional[int] = None,
    ):
        renderer = self.get_renderer(template)
        if not renderer:
            raise ValueError(f"Unknown renderer: {renderer}")

        return renderer.render(
            self.changelog_generator.get_changelog(
                title=title,
                commit_types=commit_types,
                unreleased=unreleased,
                unreleased_version=unreleased_version,
                hide_empty_releases=hide_empty_releases,
                commit_limit=commit_limit,
            )
        )

    def render_changelog_section(
        self,
        renderer: str,
        from_version: Optional[Version] = None,
        to_version: Optional[Version] = None,
        commit_types: Optional[list[CommitType, str]] = None,
        commit_limit: Optional[int] = None,
    ):
        renderer = self.get_renderer(renderer)
        if not renderer:
            raise ValueError(f"Unknown renderer: {renderer}")
        return renderer.render_section(
            self.changelog_generator.get_changelog_section(
                from_version=from_version, to_version=to_version, commit_types=commit_types, commit_limit=commit_limit
            )
        )


def create_application(settings: Settings) -> Application:
    log_providers = [GitLogProvider(), FilesLogProvider()]
    versions_provider = GitVersionsProvider(tag_prefix=settings.tag_prefix)
    message_parser = GitMessageParser(settings)
    changelog_generator = ChangelogGenerator(
        settings=settings,
        log_providers=log_providers,
        versions_provider=versions_provider,
        message_parser=message_parser,
    )
    return Application(settings=settings, changelog_generator=changelog_generator)
