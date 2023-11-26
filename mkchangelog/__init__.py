# spdx-filecopyrighttext: 2023-present Marek Wywiał <onjinx@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import os
import sys
from typing import Optional, Sequence

from rich.console import Console

from mkchangelog.app import create_application
from mkchangelog.commands.bump import BumpCommand
from mkchangelog.commands.commit import CommitCommand
from mkchangelog.commands.generate import GenerateCommand
from mkchangelog.commands.settings import SettingsCommand
from mkchangelog.config import get_settings

logger = logging.getLogger(__file__)
env = os.getenv


def add_stdout_handler(verbosity: int):
    """Adds stdout handler with given verbosity to logger.

    Args:
        logger (Logger) - python logger instance
        verbosity (int) - target verbosity
                          1 - ERROR
                          2 - INFO
                          3 - DEBUG

    Usage:
        add_stdout_handler(verbosity=3)

    """

    v_map = {1: logging.ERROR, 2: logging.INFO, 3: logging.DEBUG}
    level = v_map.get(verbosity, 1)
    logging.basicConfig(level=level)


def main(argv: Optional[Sequence[str]] = None):
    prog = "mkchangelog"
    description = "Manage CHANGELOG and versions"

    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument(
        "-v",
        "--verbosity",
        action="store",
        default=1,
        type=int,
        help="verbosity level, 1 - (ERROR, default), 2 - (INFO) or 3 - (DEBU)",
        choices=[1, 2, 3],
    )
    parser.add_argument(
        "-e",
        "--raise-exceptions",
        action="store_true",
        help="raise exceptions instead of printing only message to stderr",
    )

    subparsers = parser.add_subparsers(title="command", dest="command")

    settings = get_settings()

    for cmd in [BumpCommand, CommitCommand, GenerateCommand, SettingsCommand]:
        cmd.register(subparsers)

    args = parser.parse_args(argv)
    if args.command:
        add_stdout_handler(int(args.verbosity))
        app = create_application(settings)
        try:
            args.command(args, app)
        except Exception as exc:
            if args.raise_exceptions:
                raise
            else:
                console = Console(file=sys.stderr)
                console.print(f"[red]{exc.__class__.__name__}: {exc}")
    else:
        parser.print_help()
