from __future__ import annotations

import argparse

from mkchangelog.commands import Command
from mkchangelog.output import get_markdown_changelog, print_markdown
from mkchangelog.parser import TYPES


class GenerateCommand(Command):
    """Manage version."""

    name = "generate"
    aliases = ("g", "gen")

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            "-c",
            "--cli",
            action="store_true",
            help="mark output as CLI (colored markdown)",
            default=False,
        )
        parser.add_argument(
            "--head-name",
            action="store",
            help="custom unreleased version name",
            default=None,
        )
        parser.add_argument(
            "--header",
            action="store",
            help="changelog header, default 'Changelog'",
            default="Changelog",
        )
        parser.add_argument(
            "-m",
            "--max-count",
            action="store",
            help="limit parsed lines, default 1000",
            default=1000,
        )
        parser.add_argument(
            "-p",
            "--prefix",
            action="store",
            help="version tag prefix; default 'v'",
            default="v",
        )
        parser.add_argument(
            "-t",
            "--types",
            action="store",
            help="limit types",
            nargs="+",
            type=str,
            default=["fix", "feat"],
            choices=[*TYPES.keys(), "all"],
        )

    def execute(self):
        changelog = get_markdown_changelog(
            header=self.options.header,
            tag_prefix=self.options.prefix,
            commit_types=self.options.types,
            max_count=self.options.max_count,
            head_name=self.options.head_name,
        )
        print_markdown(changelog, colors=self.options.cli)
