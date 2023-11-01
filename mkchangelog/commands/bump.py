from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import Dict

import semver
from git import Repo

from mkchangelog.app import Application
from mkchangelog.commands import Command
from mkchangelog.config import Settings
from mkchangelog.core import (
    DATE_FORMAT,
    TZ_INFO,
    get_next_version,
)
from mkchangelog.models import Version
from mkchangelog.renderers import RENDERERS
from mkchangelog.utils import (
    print_blue,
    print_green,
    print_orange,
    yes_or_no,
)


def create_tag(name: str, message: str):
    repo = Repo(".")
    repo.create_tag(name, message=message)


def git_commit(files: list[str], message: str):
    repo = Repo(".")
    index = repo.index
    index.add(files)
    index.commit(message)


class BumpCommand(Command):
    """Manage version."""

    name = "bump"
    aliases = ("b",)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, settings: Settings):
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
            "-of",
            "--output-file",
            action="store",
            help="output changelog file; default CHANGELOG. + renderer extension",
            default=None,
        )
        parser.add_argument(
            "-p",
            "--prefix",
            action="store",
            help=f"version tag prefix; default '{settings.git_tag_prefix}'",
            default=settings.git_tag_prefix,
        )
        parser.add_argument(
            "-s",
            "--set-version",
            action="store",
            help="force version instead of detecting",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="just show versions",
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
        version = app.changelog_generator.versions_provider.get_last_version()
        if version:
            version_name = version.name
            version_date = version.date.strftime(DATE_FORMAT)
            rev = f"HEAD...{version_name}"
        else:
            version_name = f"{args.prefix}0.0.0"
            version_date = datetime.now(tz=TZ_INFO).strftime(DATE_FORMAT)
            rev = "HEAD"

        print_blue(f"Current version: {version_name} ({version_date})")
        commits = app.changelog_generator.log_provider.get_log(
            max_count=args.max_count,
            rev=rev,
        )
        commits = app.changelog_generator.get_loglines(commits, strict=False)

        if args.set_version:
            next_version = Version(
                name=f"{args.prefix}{args.set_version}",
                date=datetime.now(tz=TZ_INFO),
                semver=semver.Version.parse(args.set_version),
            )
        else:
            next_version = get_next_version(
                tag_prefix=args.prefix,
                current_version=version_name,
                commits=commits,
            )

        if next_version:
            print_green(f"Next version:    {next_version.name} ({next_version.date.strftime(DATE_FORMAT)})")
        else:
            sys.stdout.write("--> No next version available")
            return

        output_file = args.output_file
        if not output_file:
            exts: Dict[str, str] = {"markdown": "md", "rst": "rst", "json": "json"}
            ext = exts[args.renderer]
            output_file = f"CHANGELOG.{ext}"

        print_green(f"Output file:     {output_file}")

        if args.dry_run:
            return
        changelog_str = app.render_changelog(renderer=args.renderer, commit_types=args.commit_types)
        if yes_or_no(
            "--> Show next version changelog?",
            default="no",
        ):
            sys.stdout.write(changelog_str)

        ### Generate Changelog File
        if not yes_or_no(
            f"--> Generate {output_file}?",
            default="no",
        ):
            print_orange("Exiting")
            return

        # generate changelog for current version
        print_green(f"Generating:      {output_file}")
        with open(output_file, "w") as fh:
            fh.write(changelog_str)

        ### Commit & Tag new version
        if not yes_or_no(
            f"--> Commit {output_file} and tag next version {next_version.name}?",
            default="no",
        ):
            print_orange("Exiting")
            return
        print_green(f"Commiting:       {output_file}")
        # commit CHANGELOG.md
        git_commit(
            files=[output_file],
            message=f"chore(changelog): write {output_file} for version {next_version.name}",
        )

        # tag version
        print_green(f"Creating tag:    {next_version.name}")
        # create tag with "chore(version): new version v1.1.1"
        create_tag(
            name=next_version.name,
            message=f"chore(version): bump version {next_version.name}",
        )
