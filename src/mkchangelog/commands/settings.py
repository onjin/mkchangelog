from __future__ import annotations

import argparse
import json
import sys

from rich import print_json

from mkchangelog.app import Application
from mkchangelog.commands import Command
from mkchangelog.config import generate_config


class SettingsCommand(Command):
    """Manage settings."""

    name = "settings"
    aliases = ("s",)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--generate",
            action="store_true",
            help="Generate default config on the screen",
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application):
        if args.generate:
            config = generate_config()
            config.write(sys.stdout)
        else:
            print_json(json.dumps(app.settings.as_dict()))
