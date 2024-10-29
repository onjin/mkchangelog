from __future__ import annotations

import copy
import sys
from datetime import datetime, tzinfo
from functools import partial
from typing import List, Optional

import semver

try:
    import rich

    use_colors = True
except ImportError:
    rich = None
    use_colors = False

TZ_INFO: Optional[tzinfo] = datetime.now().astimezone().tzinfo


def print_color(color: str, text: str):
    if use_colors:
        from rich.console import Console

        Console().print(f"[{color}]{text}[/{color}]")
    else:
        sys.stdout.write(text)


print_blue = partial(print_color, "blue")
print_green = partial(print_color, "green")
print_orange = partial(print_color, "orange")


def create_version(prefix: str, version: str) -> semver.Version:
    """Convert version name to semantic version

    Args:
        prefix (str): version tags prefix
        version (str): version name to convert

    Returns:
        semver.Semver - semantic version object
    """
    return semver.Version.parse(version[len(prefix) :], optional_minor_and_patch=True)


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        msg = f"invalid truth value {val!r}"
        raise ValueError(msg)


def choice(question: str, choices: List[str], default: Optional[str] = None) -> str:
    """Ask for choice.

    Args:
        question (str): question to display
        choices (list[str]): list of available choices
        default (str, optional): default answer

    Returns:
        str - selected choice
    """
    display_choices: List[str] = copy.copy(choices)
    if default:
        display_choices[display_choices.index(default)] = default.upper()

    prompt = f"{question} [{','.join(display_choices)}]: "

    while True:
        sys.stdout.write(prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return default
        if choice not in choices:
            continue
        return choice


def yes_or_no(question: str, default: Optional[str] = "no") -> bool:
    """Ask question and wait for yes or no decision.

    Args:
        question (str): question to display
        default (str, optional): default answer

    Returns:
        bool - according to user answer
    """
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return strtobool(default)
        try:
            return strtobool(choice)
        except ValueError:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")
