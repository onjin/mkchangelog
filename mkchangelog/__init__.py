# spdx-filecopyrighttext: 2023-present Marek Wywiał <onjinx@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import os
import re
import sys
from abc import abstractmethod
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from io import StringIO
from itertools import groupby, tee
from operator import attrgetter
from typing import Dict, Iterator, List, NoReturn, Optional, Set, Tuple

import semver
from git import Commit, Repo

try:
    import rich

    use_colors = True
except ImportError:
    rich = None
    use_colors = False

TZ_INFO = datetime.now().astimezone().tzinfo

logger = logging.getLogger(__file__)
env = os.getenv


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def print_markdown(markdown: str, *, colors: bool = False):
    if colors and use_colors:
        from rich.console import Console
        from rich.markdown import Markdown

        console = Console()
        md = Markdown(markdown)
        console.print(md)
    else:
        sys.stdout.write(markdown)


def print_color(color: str, text: str):
    if use_colors:
        from rich.console import Console

        Console().print(f"[{color}]{text}[/{color}]")
    else:
        sys.stdout.write(text)


print_blue = partial(print_color, "blue")
print_green = partial(print_color, "green")
print_orange = partial(print_color, "orange")


COMMANDS = {}
ALIASES = {}

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Regexp for commit subject
CC_REGEXP = re.compile(r"^(?P<revert>revert: |Revert \")?(?P<type>[a-z0-9]+)(?P<scope>\([ \w]+\))?: (?P<title>.*)$")

# Regex for BREAKING CHANGE section
BC_REGEXP = re.compile(
    r"(?s)BREAKING CHANGE:(?P<breaking_change>.*?)(?:(?:\r*\n){2})",
    re.MULTILINE,
)

# Regex for Requires trailer for manual actions requiremenets
REQ_REGEXP = re.compile(
    r"(?s)Requires:(?P<requires>.*?)(?:(?:\r*\n){2})",
    re.MULTILINE,
)


REFERENCE_ACTIONS = ["Closes", "Relates"]
REF_REGEXP = re.compile(
    r"^\s+?(?P<action>{actions})\s+(?P<refs>.*)$".format(actions="|".join(REFERENCE_ACTIONS)),
    re.MULTILINE,
)

TYPES = {
    "build": "Build",
    "chore": "Chore",
    "ci": "CI",
    "dev": "Dev",
    "docs": "Docs",
    "feat": "Features",
    "fix": "Fixes",
    "perf": "Performance",
    "refactor": "Refactors",
    "style": "Style",
    "test": "Test",
    "translations": "Translations",
}
# default priority is 10 so we need only
ORDERING = {
    "feat": 10,
    "fix": 20,
    "refactor": 30,
}


@dataclass(frozen=True)
class LogLine:
    subject: str
    message: str
    revert: bool
    commit_type: str
    scope: str
    title: str
    references: List[str]
    breaking_change: List[str]


@dataclass(frozen=True)
class MatchedLine:
    log: str
    groups: str


@dataclass(frozen=True)
class Version:
    name: str
    date: datetime
    semver: str


def yes_or_no(question: str, default: Optional[str] = "no") -> bool:
    """Ask question and wait for yes or no decision.

    Args:
        question (str): question to display
        default (str, optional): default answer

    Returns:
        bool - according to user answer
    """
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return strtobool(default)
        try:
            return strtobool(choice)
        except ValueError:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


def group_commits_by_type(commits: Iterator[Commit]):
    return groupby(
        sorted(commits, key=lambda x: ORDERING.get(x.commit_type, 50)),
        attrgetter("commit_type"),
    )


def get_references_from_msg(msg: bytes) -> Dict[str, Set[str]]:
    """Get references from commit message

    Args:
        msg (str): commit message


    Returns:
        dict[set] - dictionary with references

        example:
            {
                "Closes": set("ISS-123", "ISS-321")
            }
    """
    result = REF_REGEXP.findall(msg.decode("utf-8"))
    if not result:
        return None

    refs: Dict[str, Set[str]] = defaultdict(set)
    for line in result:
        action, value = line
        for ref in value.split(","):
            refs[action].add(ref.strip())
    return refs


def add_stdout_handler(logger: logging.Logger, verbosity: int) -> NoReturn:
    """Adds stdout handler with given verbosity to logger.

    Args:
        logger (Logger) - python logger instance
        verbosity (int) - target verbosity
                          1 - ERROR
                          2 - INFO
                          3 - DEBUG

    Usage:
        add_stdout_handler(logger=logger, verbosity=3)

    """

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    v_map = {1: logging.ERROR, 2: logging.INFO, 3: logging.DEBUG}
    level = v_map.get(verbosity, 1)
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)


def v2s(prefix: str, version: str) -> semver.Version:
    """Convert version name to semantic version

    Args:
        prefix (str): version tags prefix
        version (str): version name to convert

    Returns:
        semver.Semver - semantic version object
    """
    return semver.Version.parse(version[len(prefix) :])


def get_git_versions(tag_prefix: str) -> List[semver.Version]:
    """Return versions lists

    Args:
        tag_prefix (str): versions tags prefix

    Returns:
        list(Version(name, date))
    """
    repo = Repo(".")
    versions = [
        Version(
            name=tag.name,
            date=tag.commit.authored_datetime,
            semver=v2s(tag_prefix, tag.name),
        )
        for tag in repo.tags
        if tag.name.startswith(tag_prefix)
    ]
    return sorted(versions, key=lambda v: v.date, reverse=True)


def get_last_version(tag_prefix: str) -> Optional[Version]:
    """Return last bumped bersion

    Args:
        tag_prefix (str): version tags prefix

    Returns:
        Version(name, date)
    """
    versions = get_git_versions(tag_prefix=tag_prefix)
    if not len(versions):
        return None
    return versions[0]


def get_next_version(tag_prefix: str, current_version: str, commits: List[LogLine]) -> Optional[Version]:
    """Return next version or None if not available

    Args:
        tag_prefix (str): version tags prefix
        current_version (str): current version, f.i. v1.1.1
        commits (list): list of LogLine containing commits till current version

    Returns:
        Version | None - next version object or None if no new version is available.
    """
    next_version = v2s(tag_prefix, current_version)
    current_version = str(next_version)

    # count types {{{
    types: dict[str, int] = Counter()
    for commit in commits:
        types[commit.commit_type] += 1
        if commit.breaking_change:
            types["breaking_change"] += 1
    # count types }}}

    # bump version {{{
    breaking_change: int = types.get("breaking_change", 0)
    if breaking_change > 0:
        next_version = next_version.bump_major()
    elif "feat" in types.keys():
        next_version = next_version.bump_minor()
    elif "fix" in types.keys():
        next_version = next_version.bump_patch()
    # bump version }}}

    # make next version {{{
    if semver.compare(current_version, str(next_version)) == 0:
        return None
    name = f"{tag_prefix}{next_version!s}"
    return Version(name=name, date=datetime.now(tz=TZ_INFO), semver=next_version)


def get_git_log(max_count: int = 1000, rev: Optional[str] = None, types: Optional[List[str]] = None):
    """Return git log parsed using Conventional Commit format.

    Args:
        max_count (int, optional): max lines to parse
        rev (str, optional): git rev as branch name or range
    """
    repo = Repo(".")
    commits = repo.iter_commits(max_count=max_count, no_merges=True, rev=rev)
    cc_commits = (MatchedLine(c, CC_REGEXP.match(c.summary).groupdict()) for c in commits if CC_REGEXP.match(c.summary))
    messages = (
        LogLine(
            subject=line.log.summary.encode(line.log.encoding),
            message=line.log.message.encode(line.log.encoding),
            revert=True if line.groups["revert"] else False,
            commit_type=line.groups["type"],
            scope=line.groups["scope"][1:-1] if line.groups["scope"] else line.groups["scope"],
            title=line.groups["title"],
            references=get_references_from_msg(line.log.message.encode(line.log.encoding)),
            breaking_change=(BC_REGEXP.findall(line.log.message) or [None])[0],
        )
        for line in cc_commits
    )
    if types and "all" not in types:
        log_types = types
    else:
        log_types = TYPES.keys()
    messages = (line for line in messages if line.commit_type in log_types)
    return messages


def create_tag(name, message):
    repo = Repo(".")
    repo.create_tag(name, message=message)


def git_commit(files, message):
    repo = Repo(".")
    index = repo.index
    index.add(files)
    index.commit(message)


def get_markdown_version(from_version, to_version, commit_types, max_count, output=None):
    """Return single version changelog as markdown

    Args:
        from_version (Version): starting version
        to_version (Version|None): ending version
        commit_types (list[str]): commit types to include in changelog
        max_count (int): max number of commits to parse
        output (buf, optional): buffer to write result to
    """
    if output is None:
        output = StringIO()

    if not from_version:
        from_version = "HEAD"
    if to_version:
        rev = f"{from_version}...{to_version}"
    else:
        rev = f"{from_version}"

    logger.debug(f"getting log for rev {rev} with types {commit_types}")
    lines = list(get_git_log(max_count=max_count, rev=rev, types=commit_types))
    if lines:
        # separate reverts, breaking changes {{{
        commits, reverts, breaking_changes = tee(lines, 3)

        commits = filter(lambda l: l.revert is False, commits)
        reverts = list(filter(lambda l: l.revert is True, reverts))
        breaking_changes = list(filter(lambda l: l.breaking_change, breaking_changes))
        # separate reverts, breaking changes }}}

        # group commits by type {{{
        groups = group_commits_by_type(commits)
        # group commits by type }}}
        for group_name, rows in groups:
            output.write(f"### {TYPES.get(group_name, group_name.capitalize())}\n")
            output.write("\n")
            for row in sorted(rows, key=lambda i: i.scope if i.scope else ""):
                if row.scope:
                    output.write(f"* **{row.scope}:** {row.title}")
                else:
                    output.write(f"* {row.title}")
                if row.references and "Closes" in row.references:
                    output.write(" (closes {refs})".format(refs=", ".join(row.references["Closes"])))
                output.write("\n")
            output.write("\n")

        if reverts:
            output.write("### Reverts\n")
            output.write("\n")
            for row in reverts:
                output.write(f"* {row.subject}\n")
            output.write("\n")

        if breaking_changes:
            output.write("### BREAKING CHANGES\n")
            output.write("\n")
            for row in breaking_changes:
                msg = row.breaking_change.replace("\n", " ")
                if row.scope:
                    output.write(f"* **{row.scope}**: {msg}\n")
                else:
                    output.write("* {breaking_change}\n".format())
            output.write("\n")

        output.write("\n")
        return output


def get_markdown_changelog(header, tag_prefix, commit_types, max_count, head_name=None):
    """Generate changelog in markdown format from git history

    Args:
        header (str): header text
        tag_prefix (str): version tags prefix
        commit_types (list): list of commit types to include in changelog
        max_count (int): max commit lines to parse
        head_name (str|optional): custom HEAD name, used to generate for next version

    Returns:
        str - changelog in markdown format
    """
    output = StringIO()

    output.write(f"# {header}\n\n")
    versions = get_git_versions(tag_prefix=tag_prefix)
    logger.debug(f"got versions: {versions}")

    if not versions:
        return output.read()

    # get unreleased changes {{{
    from_version = Version(
        name="HEAD",
        date=datetime.now(),
        semver=None,
    )
    to_version = versions.pop(0)

    output.write(f"## {head_name or from_version.name} ({from_version.date.strftime(DATE_FORMAT)})\n")
    output.write("\n")

    get_markdown_version(
        from_version=from_version.name,
        to_version=to_version.name,
        commit_types=commit_types,
        max_count=max_count,
        output=output,
    )
    # get unreleased changes }}}

    from_version = to_version
    for to_version in versions:
        output.write(f"## {from_version.name} ({from_version.date.strftime(DATE_FORMAT)})\n")
        output.write("\n")

        get_markdown_version(
            from_version=from_version.name,
            to_version=to_version.name,
            commit_types=commit_types,
            max_count=max_count,
            output=output,
        )

        from_version = to_version

    output.write(f"## {from_version.name} ({from_version.date.strftime(DATE_FORMAT)})\n")
    output.write("\n")
    get_markdown_version(
        from_version=from_version.name,
        to_version=None,
        commit_types=commit_types,
        max_count=max_count,
        output=output,
    )

    output.seek(0)
    return output.read()


def register_command(target_class):
    """Register command for it's name and aliases

    Args:
        target_class (Command): command to register
    """
    COMMANDS[target_class.name] = target_class
    ALIASES[target_class.name] = target_class
    for alias in target_class.aliases:
        ALIASES[alias] = target_class


class MetaRegistry(type):
    """Meta class for Command subclasses to auto register them."""

    def __new__(meta, name, bases, class_dict):
        cls = type.__new__(meta, name, bases, class_dict)
        if name != "Command" and name not in COMMANDS:
            register_command(cls)
        return cls


class Command(metaclass=MetaRegistry):
    """Base Command class."""

    name: str = "base"
    aliases: Tuple[str]

    def __init__(self, options: argparse.Namespace):
        self.options = options
        self.aliases = ()

    @staticmethod
    @abstractmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        raise NotImplementedError

    def execute(self) -> None:
        raise NotImplementedError


class BumpCommand(Command):
    """Manage version."""

    name = "bump"
    aliases = ("b",)

    @staticmethod
    def add_arguments(parser):
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
            "-t",
            "--types",
            action="store",
            help="limit types",
            nargs="+",
            type=str,
            default=["all"],
            choices=[*TYPES.keys(), "all"],
        )

    def execute(self):
        version = get_last_version(tag_prefix=self.options.prefix)
        if version:
            version_name = version.name
            version_date = version.date.strftime(DATE_FORMAT)
            rev = (f"HEAD...{version_name}",)
        else:
            version_name = f"{self.options.prefix}0.0.0"
            version_date = datetime.now(tz=TZ_INFO).strftime(DATE_FORMAT)
            rev = "HEAD"

        print_blue(f"Current version: {version_name} ({version_date})")
        commits = get_git_log(
            max_count=self.options.max_count,
            rev=rev,
            types=self.options.types,
        )

        next_version = get_next_version(
            tag_prefix=self.options.prefix,
            current_version=version_name,
            commits=commits,
        )

        if next_version:
            print_green(f"Next version:    {next_version.name} ({next_version.date.strftime(DATE_FORMAT)})")
        else:
            sys.stdout.write("--> No next version available")
            return

        if yes_or_no(
            "--> Show next version changelog?",
            default="no",
        ):
            output = StringIO()
            get_markdown_version(
                from_version="HEAD",
                to_version=version_name,
                commit_types=self.options.types,
                max_count=self.options.max_count,
                output=output,
            )
            output.seek(0)
            print_markdown(output.read(), colors=True)

        if not yes_or_no(
            f"--> Generate {self.options.output} and tag version?",
            default="no",
        ):
            print_orange("Exiting")
            return

        # generate changelog for current version {{{
        print_green(f"Generating:      {self.options.output}")
        with open(self.options.output, "w") as output:
            output.write(
                get_markdown_changelog(
                    header=self.options.header,
                    tag_prefix=self.options.prefix,
                    commit_types=self.options.types,
                    max_count=self.options.max_count,
                    head_name=next_version.name,
                )
            )

        print_green(f"Commiting:       {self.options.output}")
        # commit CHANGELOG.md
        git_commit(
            files=[self.options.output],
            message=f"chore(changelog): write {self.options.output} for version {next_version.name}",
        )
        # generate changelog for current version }}}

        # tag version {{{
        print_green(f"Creating tag:    {next_version.name}")
        # create tag with "chore(version): new version v1.1.1"
        create_tag(
            name=next_version.name,
            message=f"chore(version): bump version {next_version.name}",
        )
        # tag version }}}


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


class ChangesCommand(Command):
    """Show changes between versions."""

    name = "changes"
    aliases = ("c",)

    @staticmethod
    def add_arguments(parser: argparse.ArgumentParser):
        parser.add_argument(
            "--header",
            action="store",
            help="display header, default 'Changes'",
            default="Changes",
        )
        parser.add_argument(
            "-c",
            "--cli",
            action="store_true",
            help="mark output as CLI (colored markdown)",
            default=False,
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
            help="limit types",
            nargs="+",
            type=str,
            default=["fix", "feat"],
            choices=[*TYPES.keys(), "all"],
        )

    def execute(self):
        output = StringIO()
        output.write(f"# {self.options.header}\n")
        output.write("\n")

        output.write(
            "## {from_version} {to_version}\n".format(
                from_version=self.options.rev_from,
                to_version=self.options.rev_to or "",
            )
        )
        output.write("\n")

        # header=self.options.header,
        get_markdown_version(
            from_version=self.options.rev_from,
            to_version=self.options.rev_to,
            commit_types=self.options.types,
            max_count=self.options.max_count,
            output=output,
        )
        output.seek(0)
        print_markdown(output.read(), colors=self.options.cli)


class AliasedSubParsersAction(argparse._SubParsersAction):
    """Custom subparser action to add support for aliasing commands."""

    old_init = staticmethod(argparse._ActionsContainer.__init__)

    @staticmethod
    def _containerInit(self, description, prefix_chars, argument_default, conflict_handler):
        AliasedSubParsersAction.old_init(self, description, prefix_chars, argument_default, conflict_handler)
        self.register("action", "parsers", AliasedSubParsersAction)

    class _AliasedPseudoAction(argparse.Action):
        def __init__(self, name, aliases, help):
            dest = name
            if aliases:
                dest += " (%s)" % ",".join(aliases)
            sup = super(AliasedSubParsersAction._AliasedPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help)

    def add_parser(self, name, **kwargs):
        aliases = kwargs.pop("aliases", [])
        parser = super(AliasedSubParsersAction, self).add_parser(name, **kwargs)

        # Make the aliases work.
        for alias in aliases:
            self._name_parser_map[alias] = parser

        # Make the help text reflect them, first removing old help entry.
        if "help" in kwargs:
            help = kwargs.pop("help")
            self._choices_actions.pop()
            pseudo_action = self._AliasedPseudoAction(name, aliases, help)
            self._choices_actions.append(pseudo_action)

        return parser


# override argparse to register new subparser action by default
argparse._ActionsContainer.__init__ = AliasedSubParsersAction._containerInit


def get_command_class(input):
    """Return command class for given input

    Args:
        input (str): input command line

    Returns:
        Command - matching command
    """
    return ALIASES.get(input)


def main():
    prog = "changelog"
    description = "Manage CHANGELOG and versions"

    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store",
        default=1,
        help="verbosity level, 1 (default), 2 or 3)",
    )

    subparsers = parser.add_subparsers(title="command", dest="command")

    for cmd in COMMANDS.values():
        subparser = subparsers.add_parser(name=cmd.name, help=cmd.__doc__, aliases=cmd.aliases)
        cmd.add_arguments(subparser)

    options = parser.parse_args()

    add_stdout_handler(logger, int(options.verbosity))

    # find command using name or alias and create instance with passed arg options
    command_class = get_command_class(options.command)
    if command_class:
        command = command_class(options)
        command.execute()
    else:
        parser.print_help(sys.stderr)
