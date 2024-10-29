from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from rich import print_json

from mkchangelog.commands import Command
from mkchangelog.config import generate_config

if TYPE_CHECKING:
    import argparse

    from mkchangelog.app import Application


class SettingsCommand(Command):
    """Manage settings."""

    name = "settings"
    aliases = ("s",)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--generate",
            action="store_true",
            help="Generate default config on the screen",
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application) -> None:
        if args.generate:
            config = generate_config()
            config.write(sys.stdout)
        else:
            print_json(json.dumps(app.settings.as_dict()))
