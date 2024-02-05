import re
from typing import Any, Callable, Dict, List

import pluggy

from mkchangelog.config import Settings
from mkchangelog.exceptions import MKChangelogTemplateError
from mkchangelog.models import LogLine

hookimpl = pluggy.HookimplMarker("mkchangelog")


def underline_filter(line: str, char: str) -> str:
    return f"{line}\n{ char * len(line)}"


def regex_replace_filter(
    value: str = "",
    pattern: str = "",
    replacement: str = "",
    ignorecase: bool = False,  # noqa: FBT001, FBT002
    multiline: bool = False,  # noqa: FBT001, FBT002
    count: int = 0,
    mandatory_count: int = 0,
) -> str:
    """Perform a `re.sub` returning a string"""

    flags = 0
    if ignorecase:
        flags |= re.I
    if multiline:
        flags |= re.M
    _re = re.compile(pattern, flags=flags)
    (output, subs) = _re.subn(replacement, value, count=count)
    if mandatory_count and mandatory_count != subs:
        raise MKChangelogTemplateError(
            "'%s' should match %d times, but matches %d times in '%s'" % (pattern, mandatory_count, count, value)
        )
    return output


@hookimpl
def provide_template_filters(settings: Settings) -> Dict[str, Callable[[Any], str]]:  # noqa: ARG001
    return {"underline": underline_filter, "regex_replace": regex_replace_filter}


@hookimpl
def provide_changelog_loglines_filter(settings: Settings) -> Callable[[List[LogLine]], List[LogLine]]:  # noqa: ARG001
    return lambda loglines: loglines
