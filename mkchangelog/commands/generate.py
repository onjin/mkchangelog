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
            "--unreleased-name",
            action="store",
            help="custom unreleased version name; default 'Unreleased'",
            default="Unreleased",
        )
        parser.add_argument(
            "--include-unreleased",
            action="store_true",
            help="include unreleased changes in changelog",
            default=False,
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
        parser.add_argument(
            "--template",
            action="store",
            help="template to render changelog",
            default=settings.default_template,
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application):
        if args.template and args.renderer != "template":
            sys.stderr.write("ERROR: The '--template' option is only supported with 'template' renderer.\n")
            return
        if not args.template and args.renderer == "template":
            sys.stderr.write("ERROR: The '--template' option is required with 'template' renderer.\n")
            return
        sys.stdout.write(
            app.render_changelog(
                renderer=args.renderer,
                template=args.template,
                commit_types=args.commit_types,
                include_unreleased=args.include_unreleased,
                unreleased_name=args.unreleased_name,
            )
        )
