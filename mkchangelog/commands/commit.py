from __future__ import annotations

import argparse
from typing import List

from rich.console import Console
from rich.prompt import Confirm, Prompt

from mkchangelog.app import Application
from mkchangelog.commands import Command


class CommitCommand(Command):
    """Generate commit message."""

    name = "commit"
    aliases = ("c",)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--stdout",
            action="store_true",
            help="Dump generated commit to standard output instead of 'message.txt'",
            default=None,
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application):
        console = Console()
        console.print("[green]Git Commit Format: type(scope): summary")
        console.print()

        # 1. [req] ask for commit type
        commit_type = Prompt.ask("Commit Type", choices=list(app.settings.commit_types.keys()), default="feat")

        # 2. [opt] ask for scope
        scope = Prompt.ask("Scope: (optional)")

        # 3. [req] ask for summary
        summary = ""
        while summary == "":
            summary = Prompt.ask("Summary line")

        # 4. [req] ask if breaking change [true/false]
        is_breaking_change = Confirm.ask("Is breaking change?")

        # 5. [opt] ask for breaking change description
        if is_breaking_change:
            breaking_change = ""
            while breaking_change == "":
                breaking_change = Prompt.ask("Breaking change description")
        else:
            breaking_change = None
        # 6. [opt] ask for description (body)
        body = Prompt.ask("Long description (body)")

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

        console.print("[green]---")
        if args.stdout:
            console.print("\n".join(lines))
            console.print()
        else:
            with open("message.txt", "w") as fh:
                fh.write("\n".join(lines))
            console.print("[green]The 'message.txt' file was generated. You can edit it or just")
            console.print("[green]type 'git commit -F message.txt' to use generated message.")
        console.print("[green]---")
