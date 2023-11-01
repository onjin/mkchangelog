from __future__ import annotations

import copy
from dataclasses import dataclass
from functools import lru_cache
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


DEFAULT_SETTINGS: Dict[str, Any] = {
    "git_tag_prefix": "v",
    "changelog_title": "Changelog",
    "default_renderer": "markdown",
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


@lru_cache(maxsize=128)
def get_settings():
    conf = copy.deepcopy(DEFAULT_SETTINGS)
    # TODO: override some from .mkchangelog | .config/mkchangelog/config
    # TODO: override some from pyproject.toml
    # TODO: override some from ENV
    return Settings(**conf)
