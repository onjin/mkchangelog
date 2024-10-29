from typing import Any, Callable, Dict

import pluggy
from git import List

from mkchangelog.config import Settings
from mkchangelog.models import LogLine

hookspec = pluggy.HookspecMarker("mkchangelog")


@hookspec
def provide_template_filters(settings: Settings) -> Dict[str, Callable[[Any], str]]:
    """Return dictionary of Jinja2 filters to be used in template."""


@hookspec
def provide_changelog_loglines_filter(settings: Settings) -> Callable[[List[LogLine]], List[LogLine]]:
    """Filter changelog loglines."""
