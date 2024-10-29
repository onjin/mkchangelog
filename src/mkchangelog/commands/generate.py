from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from rich.console import Console

from mkchangelog.commands import Command

if TYPE_CHECKING:
    import argparse

    from mkchangelog.app import Application

logger = logging.getLogger()


class GenerateCommand(Command):
    """Manage version."""

    name = "generate"
    aliases = ("g", "gen")

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "-o",
            "--output",
            action="store",
            help="output file, default: CHANGELOG.[ext]",
        )
        parser.add_argument(
            "-t",
            "--template",
            action="store",
            help="specify template to use [markdown, rst, json], or path to your template default: markdown",
        )
        parser.add_argument(
            "-l",
            "--commit-limit",
            action="store",
            help="number of commits to display per release, default: 100",
            type=int,
        )
        parser.add_argument(
            "-u",
            "--unreleased",
            action="store_true",
            help="include unreleased changes in changelog",
            default=None,
        )
        parser.add_argument(
            "-uv",
            "--unreleased-version",
            action="store",
            help="use specified version as unreleased release; default 'Unreleased'",
        )
        parser.add_argument(
            "--hide-empty-releases",
            action="store_true",
            help="skip empty versions",
            default=None,
        )
        parser.add_argument(
            "--changelog-title",
            action="store",
            help="changelog title, default 'Changelog'",
        )
        parser.add_argument(
            "--tag-prefix",
            action="store",
            help="version tag prefix; default 'v'",
        )
        parser.add_argument(
            "--commit-types",
            action="store",
            dest="commit_types_list",
            help="f.e. feat,fix,refactor, all - for all convigured; default from 'commit_types_list' settings",
            nargs="+",
            type=str,
        )
        parser.add_argument(
            "-s",
            "--stdout",
            action="store_true",
            help="output changelog to stdout",
            default=None,
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application) -> None:
        options = app.settings.apply_args(args)

        logger.info("[generate] template=%s", options.template)
        logger.info("[generate] commit_types=%s", options.commit_types_list)
        logger.info("[generate] unreleased=%s", options.unreleased)
        logger.info("[generate] unreleased_version=%s", options.unreleased_version)
        logger.info("[generate] hide_empty_releases=%s", options.hide_empty_releases)

        changelog = app.render_changelog(
            title=options.changelog_title,
            template=options.template,
            commit_types=options.commit_types_list,
            unreleased=options.unreleased,
            unreleased_version=options.unreleased_version,
            hide_empty_releases=options.hide_empty_releases,
            commit_limit=options.commit_limit,
        )
        if args.stdout:
            sys.stdout.write(changelog)
        else:
            Console().print(
                f"[green]Writing changelog to {options.output} file. Use '--stdout' to print it out instead of writing."
            )
            with open(options.output, "w") as fh:
                fh.write(changelog)
