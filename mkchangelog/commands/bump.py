from __future__ import annotations

import argparse
from datetime import datetime

from git import Repo
from rich.console import Console
from rich.prompt import Confirm

from mkchangelog.app import Application
from mkchangelog.commands import Command
from mkchangelog.commands.generate import GenerateCommand
from mkchangelog.core import (
    DATE_FORMAT,
    get_next_version,
)
from mkchangelog.models import Version
from mkchangelog.utils import (
    TZ_INFO,
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
        GenerateCommand.add_arguments(parser)
        parser.add_argument(
            "-v",
            "--latest-version",
            action="store",
            help="use specified version as latest version",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="only show next version",
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application):
        console = Console()
        options = app.settings.apply_args(args, strict=False)

        version = app.changelog_generator.versions_provider.get_last_version()
        if version:
            version_name = version.name
            version_date = version.date.strftime(DATE_FORMAT)
            rev = f"HEAD...{version_name}"
        else:
            version_name = f"{options.tag_prefix}0.0.0"
            version_date = datetime.now(tz=TZ_INFO).strftime(DATE_FORMAT)
            rev = "HEAD"

        console.print(f"[green]Current version:[/green] {version_name} ({version_date})")
        commits = app.changelog_generator.get_log_messages(
            commit_limit=options.commit_limit,
            rev=rev,
        )
        commits = app.changelog_generator.get_loglines(commits, strict=False)

        if args.latest_version:
            next_version = Version.from_str(
                name=f"{options.tag_prefix}{args.latest_version}", version=args.latest_version
            )
        else:
            next_version = get_next_version(options.tag_prefix, version_name, commits)

        if next_version:
            console.print(
                f"[blue]Next version:[/blue]    {next_version.name} ({next_version.date.strftime(DATE_FORMAT)})"
            )
        else:
            console.print("[red]--> No next version available")
            return

        if args.dry_run:
            return

        changelog_str = app.render_changelog(
            title=options.changelog_title,
            template=options.template,
            commit_types=options.commit_types_list,
            unreleased=True,
            unreleased_version=next_version.name,
            hide_empty_releases=options.hide_empty_releases,
            commit_limit=options.commit_limit,
        )
        if Confirm.ask(
            "--> Show next version changelog?",
            default=False,
        ):
            console.print(changelog_str)

        ### Generate Changelog File
        if not Confirm.ask(
            f"--> Generate {options.output}?",
            default=False,
        ):
            console.print("Exiting")
            return

        # generate changelog for current version
        console.print(f"[green]Generating:[/green]      {options.output}")
        with open(options.output, "w") as fh:
            fh.write(changelog_str)

        ### Commit & Tag new version
        if not Confirm.ask(
            f"--> Commit {options.output} and tag next version {next_version.name}?",
            default=False,
        ):
            with open("message.txt", "w") as fh:
                fh.write(f"chore(changelog): write {options.output} for version {next_version.name}")
            console.print("Exiting")
            return
        console.print(f"[green]Commiting:[/green]       {options.output}")
        # commit CHANGELOG.md
        git_commit(
            files=[options.output],
            message=f"chore(changelog): write {options.output} for version {next_version.name}",
        )

        # tag version
        console.print(f"[green]Creating tag:[/green]    {next_version.name}")
        # create tag with "chore(version): new version v1.1.1"
        create_tag(
            name=next_version.name,
            message=f"chore(version): bump version {next_version.name}",
        )
