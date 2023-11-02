from __future__ import annotations

import argparse
import sys
from typing import List

from mkchangelog.app import Application
from mkchangelog.commands import Command
from mkchangelog.config import Settings
from mkchangelog.utils import choice, yes_or_no


class CommitCommand(Command):
    """Generate commit message."""

    name = "commit"
    aliases = ("c",)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, settings: Settings):  # noqa: ARG003
        parser.add_argument(
            "--stdout",
            action="store_true",
            help="Dump generated commit to standard output instead of GIT_COMMIT_MESSAGE",
            default=None,
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application):
        sys.stdout.write("Git Commit Format: type(scope): summary\n\n")

        # 1. [req] ask for commit type
        commit_type = choice("Commit Type", choices=list(app.settings.commit_types.keys()), default="feat")

        # 2. [opt] ask for scope
        scope = input("Scope: (optional): ")

        # 3. [req] ask for summary
        summary = input("Summary line: ")

        # 4. [req] ask if breaking change [true/false]
        is_breaking_change = yes_or_no("Is breaking change?")

        # 5. [opt] ask for breaking change description
        if is_breaking_change:
            breaking_change = input("Breaking change description: ")
        else:
            breaking_change = None
        # 6. [opt] ask for description (body)
        body = input("Long description (body): ")

        # 7. [opt] ask for footer key: values
        # 8. write to output
        commit = f"{commit_type}"
        if scope:
            commit += f"({scope})"
        if is_breaking_change:
            commit += "!"
        commit += f": {summary}"
        footer_lines: List[str] = []
        if breaking_change:
            footer_lines.append(f"BREAKING CHANGE: {breaking_change}")

        lines = [commit]
        if body:
            lines.extend(["", body])
        if footer_lines:
            lines.append("")
            lines.extend(footer_lines)

        sys.stdout.write("---\n")
        if args.stdout:
            sys.stdout.write("\n".join(lines))
            sys.stdout.write("\n")
        else:
            with open("message.txt", "w") as fh:
                fh.write("\n".join(lines))
            sys.stdout.write("The 'message.txt' file was generated. You can edit it or just\n")
            sys.stdout.write("type 'git commit -F message.txt' to use generated message\n")
        sys.stdout.write("---\n")
