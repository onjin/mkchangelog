from __future__ import annotations

import configparser
import copy
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from mkchangelog.models import CommitType


@dataclass(frozen=True)
class Settings:
    git_tag_prefix: str
    changelog_title: str
    default_renderer: str
    # used for `all` to check valid types, and to provide
    # header's names - used in ChangelogRenderers
    commit_types: Dict[CommitType, str]
    short_commit_types_list: List[str]

    # used to prioritize commit types section
    # - used in ChangelogRenderers
    commit_type_default_priority: int
    commit_types_priorities: Dict[CommitType, str]

    default_template: str = ""


DEFAULT_SETTINGS: Dict[str, Any] = {
    "git_tag_prefix": "v",
    "changelog_title": "Changelog",
    "default_renderer": "markdown",
    "default_template": "",
    "commit_types": {
        "build": "Build",
        "chore": "Chore",
        "ci": "CI",
        "dev": "Dev",
        "docs": "Docs",
        "feat": "Features",
        "fix": "Fixes",
        "perf": "Performance",
        "refactor": "Refactors",
        "style": "Style",
        "test": "Test",
        "translations": "Translations",
    },
    "short_commit_types_list": ["fix", "feat"],
    "commit_type_default_priority": 10,
    "commit_types_priorities": {
        "feat": 40,
        "fix": 30,
        "refactor": 20,
    },
}


def read_ini_settings(path: str) -> Dict[str, Any]:
    plain_options = [
        ("changelog_title", str),
        ("commit_type_default_priority", int),
        ("default_renderer", str),
        ("default_template", str),
        ("git_tag_prefix", str),
    ]
    list_options = [
        ("short_commit_types_list", str),
    ]
    dict_options = [
        ("commit_types", str),
        ("commit_types_priorities", int),
    ]
    settings: Dict[str, Any] = {}

    path = Path(path)
    config = configparser.ConfigParser()
    config.read(path)
    if "GENERAL" in config:
        general = config["GENERAL"]
        for key, opt_type in plain_options:
            if key in general:
                settings[key] = opt_type(general[key])
        for key, opt_type in list_options:
            if key in general:
                settings[key] = [opt_type(opt) for opt in general[key].split(",")]
    for key, opt_type in dict_options:
        if key not in config:
            continue
        section = config[key]
        option = {}
        for opt, value in section.items():
            option[opt] = opt_type(value)
        settings[key] = option

    return settings


@lru_cache(maxsize=128)
def get_settings():
    conf = copy.deepcopy(DEFAULT_SETTINGS)
    conf.update(read_ini_settings(".mkchangelog"))
    # TODO: override some from .mkchangelog | .config/mkchangelog/config
    # TODO: override some from pyproject.toml
    # TODO: override some from ENV
    return Settings(**conf)
