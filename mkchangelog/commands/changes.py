from __future__ import annotations

import argparse
import sys

from mkchangelog.app import Application
from mkchangelog.commands import Command
from mkchangelog.config import Settings
from mkchangelog.models import Version
from mkchangelog.renderers import RENDERERS


class ChangesCommand(Command):
    """Show changes between versions."""

    name = "changes"
    aliases = ("c",)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, settings: Settings):
        parser.add_argument(
            "--header",
            action="store",
            help="display header, default 'Changes'",
            default="Changes",
        )
        parser.add_argument(
            "-m",
            "--max-count",
            action="store",
            help="limit parsed lines, default 1000",
            default=1000,
        )
        parser.add_argument(
            "--rev-from",
            action="store",
            help="limit newest revision (tag/hash); default HEAD",
            default="HEAD",
        )
        parser.add_argument(
            "--rev-to",
            action="store",
            help="limit oldest revision (tag/hash)",
            default=None,
        )
        parser.add_argument(
            "-t",
            "--types",
            action="store",
            dest="commit_types",
            help="limit types",
            nargs="+",
            type=str,
            default=settings.short_commit_types_list,
            choices=[*settings.commit_types.keys(), "all"],
        )
        parser.add_argument(
            "-r",
            "--renderer",
            action="store",
            help="data renderer",
            choices=RENDERERS.keys(),
            default=settings.default_renderer,
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application):
        version_from = Version(args.rev_from) if args.rev_from else None
        version_to = Version(args.rev_to) if args.rev_to else None
        sys.stdout.write(
            app.render_changelog_section(
                renderer=args.renderer, from_version=version_from, to_version=version_to, commit_types=args.commit_types
            )
        )
