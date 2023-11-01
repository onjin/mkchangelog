from __future__ import annotations

import argparse
import sys

from mkchangelog.app import Application
from mkchangelog.commands import Command
from mkchangelog.config import Settings
from mkchangelog.renderers import RENDERERS


class GenerateCommand(Command):
    """Manage version."""

    name = "generate"
    aliases = ("g", "gen")

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, settings: Settings):
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
        sys.stdout.write(app.render_changelog(renderer=args.renderer, commit_types=args.commit_types))
