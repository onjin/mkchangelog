# spdx-filecopyrighttext: 2023-present Marek Wywiał <onjinx@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import os
import sys
from typing import Optional, Sequence

from mkchangelog.app import create_application
from mkchangelog.commands.bump import BumpCommand
from mkchangelog.commands.changes import ChangesCommand
from mkchangelog.commands.generate import GenerateCommand
from mkchangelog.config import get_settings

logger = logging.getLogger(__file__)
env = os.getenv


def add_stdout_handler(logger: logging.Logger, verbosity: int):
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


def main(argv: Optional[Sequence[str]] = None):
    prog = "mkchangelog"
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

    settings = get_settings()

    ChangesCommand.register(subparsers, settings)
    GenerateCommand.register(subparsers, settings)
    BumpCommand.register(subparsers, settings)

    args = parser.parse_args(argv)
    if args.command:
        add_stdout_handler(logger, int(args.verbosity))
        app = create_application(settings)
        args.command(args, app)
    else:
        parser.print_help()
