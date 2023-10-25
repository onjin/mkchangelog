# spdx-filecopyrighttext: 2023-present Marek Wywiał <onjinx@gmail.com>
#
# SPDX-License-Identifier: MIT

import argparse
import logging
import os
import sys
from typing import Optional, Sequence

from mkchangelog.commands import COMMANDS, get_command_class
from mkchangelog.commands.bump import BumpCommand
from mkchangelog.commands.changes import ChangesCommand
from mkchangelog.commands.generate import GenerateCommand

__all__ = ["BumpCommand", "ChangesCommand", "GenerateCommand", "main"]


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

    for cmd in COMMANDS.values():
        subparser = subparsers.add_parser(name=cmd.name, help=cmd.__doc__, aliases=cmd.aliases)
        cmd.add_arguments(subparser)

    options = parser.parse_args(argv)

    add_stdout_handler(logger, int(options.verbosity))

    # find command using name or alias and create instance with passed arg options
    command_class = get_command_class(options.command)
    if command_class:
        command = command_class(options)
        command.execute()
    else:
        parser.print_help(sys.stderr)
