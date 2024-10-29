from __future__ import annotations

import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import argparse

    from mkchangelog.app import Application


class Command:
    """Base Command class."""

    name: str
    aliases: tuple[str, ...]

    @classmethod
    def register(cls, subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> argparse.ArgumentParser:
        """
        Register Command to subparsers.

        Creates the subparser for command options and sets `command=cls.execute` as default
        executor.
        """
        subparser = subparsers.add_parser(name=cls.name, help=cls.__doc__, aliases=cls.aliases)
        cls.add_arguments(subparser)
        subparser.set_defaults(command=cls.execute)
        return subparser

    @classmethod
    @abc.abstractmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def execute(cls, args: argparse.Namespace, app: Application) -> None:
        raise NotImplementedError
