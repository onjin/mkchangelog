from __future__ import annotations

import argparse
import sys
from datetime import datetime
from io import StringIO

import semver
from git import Repo

from mkchangelog.commands import Command
from mkchangelog.core import (
    DATE_FORMAT,
    TZ_INFO,
    get_next_version,
)
from mkchangelog.models import TYPES, Version
from mkchangelog.output import (
    get_markdown_changelog,
    get_markdown_version,
    print_markdown,
)
from mkchangelog.parser import GitLogParser
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
    def add_arguments(cls, parser: argparse.ArgumentParser):
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
            "-o",
            "--output",
            action="store",
            help="output changelog file; default CHANGELOG.md",
            default="CHANGELOG.md",
        )
        parser.add_argument(
            "-p",
            "--prefix",
            action="store",
            help="version tag prefix; default 'v'",
            default="v",
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
            help="limit types",
            nargs="+",
            type=str,
            default=["all"],
            choices=[*TYPES.keys(), "all"],
        )

    @classmethod
    def execute(cls, args: argparse.Namespace):
        version = GitLogParser(tag_prefix=args.prefix).get_last_version()
        if version:
            version_name = version.name
            version_date = version.date.strftime(DATE_FORMAT)
            rev = f"HEAD...{version_name}"
        else:
            version_name = f"{args.prefix}0.0.0"
            version_date = datetime.now(tz=TZ_INFO).strftime(DATE_FORMAT)
            rev = "HEAD"

        print_blue(f"Current version: {version_name} ({version_date})")
        commits = GitLogParser().get_log(
            max_count=args.max_count,
            rev=rev,
            types=args.types,
        )

        if args.set_version:
            next_version = Version(
                name=f"{args.prefix}{args.set_version}",
                date=datetime.now(tz=TZ_INFO),
                semver=semver.Version.parse(args.set_version),
            )
        else:
            next_version = get_next_version(
                current_version=version_name,
                commits=commits,
            )

        if next_version:
            print_green(f"Next version:    {next_version.name} ({next_version.date.strftime(DATE_FORMAT)})")
        else:
            sys.stdout.write("--> No next version available")
            return

        if args.dry_run:
            return
        if yes_or_no(
            "--> Show next version changelog?",
            default="no",
        ):
            output = StringIO()
            get_markdown_version(
                from_version="HEAD",
                to_version=version_name,
                commit_types=args.types,
                max_count=args.max_count,
                output=output,
            )
            output.seek(0)
            print_markdown(output.read(), colors=True)

        if not yes_or_no(
            f"--> Generate {args.output} and tag version?",
            default="no",
        ):
            print_orange("Exiting")
            return

        # generate changelog for current version
        print_green(f"Generating:      {args.output}")
        with open(args.output, "w") as output:
            output.write(
                get_markdown_changelog(
                    header=args.header,
                    tag_prefix=args.prefix,
                    commit_types=args.types,
                    max_count=args.max_count,
                    head_name=next_version.name,
                )
            )

        print_green(f"Commiting:       {args.output}")
        # commit CHANGELOG.md
        git_commit(
            files=[args.output],
            message=f"chore(changelog): write {args.output} for version {next_version.name}",
        )

        # tag version
        print_green(f"Creating tag:    {next_version.name}")
        # create tag with "chore(version): new version v1.1.1"
        create_tag(
            name=next_version.name,
            message=f"chore(version): bump version {next_version.name}",
        )
