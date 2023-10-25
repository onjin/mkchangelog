import argparse
from io import StringIO

from mkchangelog.commands import Command
from mkchangelog.output import get_markdown_version, print_markdown
from mkchangelog.parser import TYPES


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
