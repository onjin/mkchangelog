from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any, Callable

from mkchangelog.lib import hookimpl

if TYPE_CHECKING:
    from mkchangelog.config import Settings
    from mkchangelog.models import LogLine


def fancylize(s):
    return "".join([c.lower() if random.randint(0, 1) else c.upper() for c in s])  # noqa: S311


@hookimpl
def provide_template_filters(settings: Settings) -> dict[str, Callable[[Any], str]]:  # noqa: ARG001
    return {"fancylize": fancylize}


@hookimpl
def provide_changelog_loglines_filter(settings: Settings) -> Callable[[list[LogLine]], list[LogLine]]:  # noqa: ARG001
    return lambda loglines: [line for line in loglines if line.scope != "hidden_scope"]
