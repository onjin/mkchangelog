from __future__ import annotations

import argparse
import json
import sys

from rich import print_json

from mkchangelog.app import Application
from mkchangelog.commands import Command
from mkchangelog.config import Settings, get_config, read_ini_settings


class ConfigCommand(Command):
    """Manage configuration."""

    name = "config"
    aliases = ("conf",)

    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, settings: Settings):  # noqa: ARG003
        parser.add_argument(
            "--generate",
            action="store_true",
            help="Generate default config on the screen",
        )

    @classmethod
    def execute(cls, args: argparse.Namespace, app: Application):  # noqa: ARG003
        if args.generate:
            config = get_config()
            config.write(sys.stdout)
        else:
            print_json(json.dumps(read_ini_settings(".mkchangelog")))
