from __future__ import annotations

import argparse
from abc import abstractmethod
from typing import Any, Dict, Optional

COMMANDS: Dict[str, Command] = {}
ALIASES: Dict[str, Command] = {}


def register_command(target_class: Command):
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

    def __new__(cls, name: str, bases: tuple[type, ...], class_dict: dict[str, Any]):
        new_cls = type.__new__(cls, name, bases, class_dict)
        if name != "Command" and name not in COMMANDS:
            register_command(new_cls)
        return new_cls


class Command(metaclass=MetaRegistry):
    """Base Command class."""

    name: str = "base"
    aliases: tuple[str]

    def __init__(self, options: argparse.Namespace):
        self.options = options
        self.aliases = ()

    @staticmethod
    @abstractmethod
    def add_arguments(parser: argparse.ArgumentParser) -> None:
        raise NotImplementedError

    def execute(self) -> None:
        raise NotImplementedError


def get_command_class(cmd: str) -> Optional[Command]:
    """Return command class for given input

    Args:
        cmd (str): input command line

    Returns:
        Command - matching command
    """
    return ALIASES.get(cmd)
