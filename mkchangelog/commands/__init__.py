from __future__ import annotations

import abc
import argparse

from mkchangelog.app import Application
from mkchangelog.config import Settings


class Command:
    """Base Command class."""

    name: str
    aliases: tuple[str, ...]

    @classmethod
    def register(cls, subparsers: argparse._SubParsersAction[argparse.ArgumentParser], settings: Settings):
        """Register Command to subparsers

        Creates the subparser for command options and sets `command=cls.execute` as default
        executor.
        """

        subparser = subparsers.add_parser(name=cls.name, help=cls.__doc__, aliases=cls.aliases)
        cls.add_arguments(subparser, settings)
        subparser.set_defaults(command=cls.execute)
        return subparser

    @classmethod
    @abc.abstractmethod
    def add_arguments(cls, parser: argparse.ArgumentParser, settings: Settings) -> None:
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def execute(cls, args: argparse.Namespace, app: Application) -> None:
        raise NotImplementedError
