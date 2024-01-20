from __future__ import annotations

import argparse
import configparser
import copy
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

from git import List

from mkchangelog.utils import strtobool

DEFAULT_SETTINGS: Dict[str, Any] = {
    "GENERAL": {
        "output": "CHANGELOG.md",
        "template": "markdown",
        "commit_limit": 100,
        "unreleased": False,
        "unreleased_version": "Unreleased",
        "hide_empty_releases": False,
        "changelog_title": "Changelog",
        "commit_types_list": ["fix", "feat"],
        "commit_type_default_priority": 10,
        "tag_prefix": "v",
        "raise_exceptions": False,
    },
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
    "commit_types_priorities": {
        "feat": 40,
        "fix": 30,
        "refactor": 20,
    },
    "reference_aliases": {
        "Closes": ["Close", "Closed"],
        "Fixes": ["Fix", "Fixed"],
        "Resolves": ["Resolve", "Resolved"],
        "Relates": ["Relate", "Related"],
    },
}


@dataclass(frozen=True)
class Settings:
    # 'stdout' or filename
    output: str = DEFAULT_SETTINGS["GENERAL"]["output"]

    # 'markdown', 'rst', 'json' or filename
    template: str = DEFAULT_SETTINGS["GENERAL"]["template"]

    # commits limit per release
    commit_limit: int = DEFAULT_SETTINGS["GENERAL"]["commit_limit"]

    # include unreleased changes
    unreleased: bool = DEFAULT_SETTINGS["GENERAL"]["unreleased"]

    # unreleased version name 'Unreleased'
    unreleased_version: str = DEFAULT_SETTINGS["GENERAL"]["unreleased_version"]

    # hide releases with no commits gathered by types
    hide_empty_releases: bool = DEFAULT_SETTINGS["GENERAL"]["hide_empty_releases"]

    # used in templates to generate main header
    changelog_title: str = DEFAULT_SETTINGS["GENERAL"]["changelog_title"]

    # git tag version prefix
    tag_prefix: str = DEFAULT_SETTINGS["GENERAL"]["tag_prefix"]

    # commit types to gather by default
    commit_types_list: list[str] = field(default_factory=lambda: DEFAULT_SETTINGS["GENERAL"]["commit_types_list"])

    # default sort priority for commit type, used to rendering
    commit_type_default_priority: int = DEFAULT_SETTINGS["GENERAL"]["commit_type_default_priority"]

    # used to prioritize commit types section
    # - used in ChangelogRenderers
    commit_types_priorities: Dict[str, str] = field(default_factory=lambda: DEFAULT_SETTINGS["commit_types_priorities"])

    # used for `all` to check valid types, and to provide
    # header's names - used in ChangelogRenderers
    commit_types: Dict[str, str] = field(default_factory=lambda: DEFAULT_SETTINGS["commit_types"])

    # used to gather references f.e. Fixed, Fix, and Fixes under single Fix key
    reference_aliases: Dict[str, str] = field(default_factory=lambda: DEFAULT_SETTINGS["reference_aliases"])

    # raise exceptions on command's errors
    raise_exceptions: bool = DEFAULT_SETTINGS["GENERAL"]["raise_exceptions"]

    @classmethod
    def from_dict(cls, d: Dict[str, Any], *, strict: bool = True) -> Settings:
        """Create settings from dictionary.

        The input dictionary must contain 'GENERAL' section.

        In strict mode will raise `ValueError` on unknown keys/sections otherwise
        the unknown keys will be skipped.

        Args:
            d: input dictionary
            strict: raise ValueError on unknown keys or skip keys

        Raises:
            ValueError: raised on unknown keys

        Returns:
            Settings
        """
        config = {}
        for section, conf in d.items():
            if section == "GENERAL":
                for key, value in conf.items():
                    if key not in Settings.__dataclass_fields__:
                        if strict:
                            raise ValueError(f"Unknown setting {key}")
                        else:
                            continue
                    config[key] = value
            else:
                if section not in Settings.__dataclass_fields__:
                    if strict:
                        raise ValueError(f"Unknown setting {section}")
                    else:
                        continue
                config[section] = conf
        return Settings(**config)

    def as_dict(self) -> Dict[str, Any]:
        config = {}
        for section, conf in DEFAULT_SETTINGS.items():
            if section == "GENERAL":
                config["GENERAL"] = {}
                for key, _ in conf.items():
                    config["GENERAL"][key] = getattr(self, key)
            else:
                config[section] = conf
        return config

    def apply_args(self, args: argparse.Namespace, *, strict: bool = True) -> Settings:
        conf = self.as_dict()
        for key, value in args._get_kwargs():
            if key in ["verbosity", "command", "stdout"]:
                continue
            if value is None:
                continue
            conf["GENERAL"][key] = value
        return Settings.from_dict(conf, strict=strict)


def generate_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()

    config.add_section("GENERAL")
    for key, value in DEFAULT_SETTINGS["GENERAL"].items():
        if isinstance(value, List):
            str_value: str = ",".join(str(v) for v in value)
        else:
            str_value = str(value)
        config.set("GENERAL", key, str_value)

    for section_name in ["commit_types", "commit_types_priorities", "reference_aliases"]:
        config.add_section(section_name)
        for key, value in DEFAULT_SETTINGS[section_name].items():
            config.set(section_name, key, str(value))
    return config


def read_ini_settings(path: str) -> Dict[str, Any]:
    settings: Dict[str, Any] = {}

    path = Path(path)
    config = configparser.ConfigParser()
    config.read(path)
    for section_name, _ in DEFAULT_SETTINGS.items():
        if section_name in config:
            section = config[section_name]
            if section_name == "GENERAL":
                settings["GENERAL"] = {}
                for key, default in DEFAULT_SETTINGS[section_name].items():
                    if key not in section:
                        continue
                    if isinstance(default, bool):
                        read_val = strtobool(section[key])
                    elif isinstance(default, list):
                        read_val = section[key].split(",")
                    else:
                        read_val = section[key]
                    settings["GENERAL"][key] = read_val
            else:
                settings[section_name] = {k: v for k, v in section.items()}  # noqa: C416
    return settings


@lru_cache(maxsize=128)
def get_settings():
    conf = copy.deepcopy(DEFAULT_SETTINGS)
    conf.update(read_ini_settings(".mkchangelog"))
    # TODO: override some from pyproject.toml
    # TODO: override some from ENV
    return Settings.from_dict(conf)
