from __future__ import annotations

import sys
from datetime import datetime, tzinfo
from typing import Optional

TZ_INFO: tzinfo = datetime.now().astimezone().tzinfo
DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


def strtobool(val: str) -> bool:
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        return 0
    else:
        msg = f"invalid truth value {val!r}"
        raise ValueError(msg)


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
