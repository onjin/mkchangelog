from __future__ import annotations

import logging
import sys
from datetime import datetime
from functools import partial
from io import StringIO
from itertools import tee
from typing import List, Optional

from mkchangelog.base import (
    DATE_FORMAT,
    TZ_INFO,
)
from mkchangelog.parser import (
    TYPES,
    Version,
    get_git_log,
    get_git_versions,
    group_commits_by_type,
)

try:
    import rich

    use_colors = True
except ImportError:
    rich = None
    use_colors = False


def print_markdown(markdown: str, *, colors: bool = False):
    if colors and use_colors:
        from rich.console import Console
        from rich.markdown import Markdown

        console = Console()
        md = Markdown(markdown)
        console.print(md)
    else:
        sys.stdout.write(markdown)


def print_color(color: str, text: str):
    if use_colors:
        from rich.console import Console

        Console().print(f"[{color}]{text}[/{color}]")
    else:
        sys.stdout.write(text)


print_blue = partial(print_color, "blue")
print_green = partial(print_color, "green")
print_orange = partial(print_color, "orange")

logger = logging.getLogger()


def get_markdown_version(
    from_version: Version, to_version: Version, commit_types: list[str], max_count: int, output=None
):
    """Return single version changelog as markdown

    Args:
        from_version (Version): starting version
        to_version (Version|None): ending version
        commit_types (list[str]): commit types to include in changelog
        max_count (int): max number of commits to parse
        output (buf, optional): buffer to write result to
    """
    if output is None:
        output = StringIO()

    if not from_version:
        from_version = "HEAD"
    if to_version:
        rev = f"{from_version}...{to_version}"
    else:
        rev = f"{from_version}"

    logger.debug(f"getting log for rev {rev} with types {commit_types}")
    lines = list(get_git_log(max_count=max_count, rev=rev, types=commit_types))
    if lines:
        # separate reverts, breaking changes {{{
        commits, reverts, breaking_changes = tee(lines, 3)

        commits = filter(lambda line: line.revert is False, commits)
        reverts = list(filter(lambda line: line.revert is True, reverts))
        breaking_changes = list(filter(lambda line: line.breaking_change, breaking_changes))
        # separate reverts, breaking changes }}}

        # group commits by type {{{
        groups = group_commits_by_type(commits)
        # group commits by type }}}
        for group_name, rows in groups:
            output.write(f"### {TYPES.get(group_name, group_name.capitalize())}\n")
            output.write("\n")
            for row in sorted(rows, key=lambda i: i.scope if i.scope else ""):
                if row.scope:
                    output.write(f"* **{row.scope}:** {row.title}")
                else:
                    output.write(f"* {row.title}")
                if row.references and "Closes" in row.references:
                    output.write(" (closes {refs})".format(refs=", ".join(row.references["Closes"])))
                output.write("\n")
            output.write("\n")

        if reverts:
            output.write("### Reverts\n")
            output.write("\n")
            for row in reverts:
                output.write(f"* {row.subject}\n")
            output.write("\n")

        if breaking_changes:
            output.write("### BREAKING CHANGES\n")
            output.write("\n")
            for row in breaking_changes:
                msg = row.breaking_change.replace("\n", " ")
                if row.scope:
                    output.write(f"* **{row.scope}**: {msg}\n")
                else:
                    output.write(f"* {msg}\n")
            output.write("\n")

        output.write("\n")
        return output


def get_markdown_changelog(
    header: str, tag_prefix: str, commit_types: List[str], max_count: int, head_name: Optional[str] = None
) -> str:
    """Generate changelog in markdown format from git history

    Args:
        header (str): header text
        tag_prefix (str): version tags prefix
        commit_types (list): list of commit types to include in changelog
        max_count (int): max commit lines to parse
        head_name (str|optional): custom HEAD name, used to generate for next version

    Returns:
        str - changelog in markdown format
    """
    output = StringIO()

    output.write(f"# {header}\n\n")
    versions = get_git_versions(tag_prefix=tag_prefix)
    logger.debug(f"got versions: {versions}")

    if not versions:
        return output.read()

    # get unreleased changes {{{
    from_version = Version(
        name="HEAD",
        date=datetime.now(tz=TZ_INFO),
        semver=None,
    )
    to_version = versions.pop(0)

    output.write(f"## {head_name or from_version.name} ({from_version.date.strftime(DATE_FORMAT)})\n")
    output.write("\n")

    get_markdown_version(
        from_version=from_version.name,
        to_version=to_version.name,
        commit_types=commit_types,
        max_count=max_count,
        output=output,
    )
    # get unreleased changes }}}

    from_version = to_version
    for to_version in versions:
        output.write(f"## {from_version.name} ({from_version.date.strftime(DATE_FORMAT)})\n")
        output.write("\n")

        get_markdown_version(
            from_version=from_version.name,
            to_version=to_version.name,
            commit_types=commit_types,
            max_count=max_count,
            output=output,
        )

        from_version = to_version

    output.write(f"## {from_version.name} ({from_version.date.strftime(DATE_FORMAT)})\n")
    output.write("\n")
    get_markdown_version(
        from_version=from_version.name,
        to_version=None,
        commit_types=commit_types,
        max_count=max_count,
        output=output,
    )

    output.seek(0)
    return output.read()
