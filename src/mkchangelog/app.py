"""The Applications object."""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

import pluggy

from mkchangelog import hookspecs, lib
from mkchangelog.core import ChangelogGenerator
from mkchangelog.parser import GitMessageParser
from mkchangelog.providers import FilesLogProvider, GitLogProvider, GitVersionsProvider
from mkchangelog.renderers import RENDERERS, ChangelogRenderer, TemplateChangelogRenderer

if TYPE_CHECKING:
    from mkchangelog.config import Settings
    from mkchangelog.models import CommitType, Version

logger = logging.getLogger()


class Application:
    """Main application code."""

    def __init__(self, *, settings: Settings, changelog_generator: ChangelogGenerator, hook: pluggy.HookRelay) -> None:
        self.settings = settings
        self.changelog_generator = changelog_generator
        self.hook = hook

    def get_renderer(self, name: str) -> ChangelogRenderer:
        """
        Get ChangelogRenderer by name.

        If renderer is not registered, then default TemplateChangelogRenderer is returned
        with passed name as input template.

        Args:
            name: template name or already registered renderer name

        Returns:
            ChangelogRenderer
        """
        try:
            renderer_class = RENDERERS[name]
            renderer = renderer_class(self.settings)
        except KeyError:
            renderer = TemplateChangelogRenderer(self.settings, name)

        # register jinja filters for TemplateChangelogRenderer instances
        if isinstance(renderer, TemplateChangelogRenderer):
            for key, tpl_filter in self.get_template_filters().items():
                logger.debug("registering filter '%s'", key)
                renderer.env.filters[key] = tpl_filter
        return renderer

    def get_template_filters(self) -> dict[str, Callable[[Any], str]]:
        """
        Returns dictionary of registered template filters.

        The final filters dictionary is merged from the default filters and from
        registered hooks.
        """
        ff = {}
        for _dict in self.hook.provide_template_filters(settings=self.settings):
            ff.update(_dict)
        return ff

    def render_changelog(
        self,
        *,
        template: str | None = None,
        title: str | None = None,
        commit_types: list[CommitType] | None = None,
        unreleased: bool = False,
        unreleased_version: str = "Unreleased",
        hide_empty_releases: bool = False,
        commit_limit: int | None = None,
    ) -> Any:
        """
        Render changelog.

        Args:
            template: optional template or registered renderer name
            title: optional changelog title
            commit_types: optional list of commit types to show in changelog
            unreleased: whether include unreleased changes in changelog; default False
            unreleased_version: unreleased changes section name; default 'Unreleased',
            hide_empty_releases: whether hide empty releases or not; default False
            commit_limit: limit of commits used to create changelog
        """
        renderer = self.get_renderer(template)
        if not renderer:
            msg = f"Unknown renderer: {renderer}"
            raise ValueError(msg)

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
        from_version: Version | None = None,
        to_version: Version | None = None,
        commit_types: list[CommitType, str] | None = None,
        commit_limit: int | None = None,
    ) -> Any:
        """Render single changelog section.

        Args:
            renderer: registered renderer name
            from_version: optional start version
            to_version: optional stop version
            commit_types: optional list of commit types to include in changelog
            commit_limit: limit of commits used to create changelog

        Returns:
            Any
        """
        renderer = self.get_renderer(renderer)
        if not renderer:
            msg = f"Unknown renderer: {renderer}"
            raise ValueError(msg)
        return renderer.render_section(
            self.changelog_generator.get_changelog_section(
                from_version=from_version, to_version=to_version, commit_types=commit_types, commit_limit=commit_limit
            )
        )


def get_plugin_manager() -> pluggy.PluginManager:
    """Return PluginManager."""
    pm = pluggy.PluginManager("mkchangelog")
    pm.add_hookspecs(hookspecs)
    pm.load_setuptools_entrypoints("mkchangelog")

    hooks_path = Path() / ".mkchangelog.d" / "hooks.py"
    if hooks_path.exists():
        spec = importlib.util.spec_from_file_location("mkchangelog_hooks", hooks_path)
        if spec and spec.loader:
            mkchangelog_hooks = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mkchangelog_hooks)
            pm.register(mkchangelog_hooks)

    # register `lib` as last (can be overwritten by custom hooks then)
    pm.register(lib)
    return pm


def create_application(settings: Settings) -> Application:
    """Create main Applicaiton.

    Args:
        settings: application settings
    """
    pm = get_plugin_manager()

    log_providers = [GitLogProvider(), FilesLogProvider()]
    versions_provider = GitVersionsProvider(tag_prefix=settings.tag_prefix)
    message_parser = GitMessageParser(settings)
    changelog_generator = ChangelogGenerator(
        settings=settings,
        log_providers=log_providers,
        versions_provider=versions_provider,
        message_parser=message_parser,
        log_filters=pm.hook.provide_changelog_loglines_filter(settings=settings),
    )
    return Application(settings=settings, changelog_generator=changelog_generator, hook=pm.hook)
