# src/context_engine/resources.py

"""Resource loading utilities for the Context Engineering Engine.

Resources (normativas, taxonomias, templates) are stored as YAML files in a
configurable directory. This module provides simple accessor functions that
read the files and cache them for fast repeated access.
"""

import os
import yaml
from typing import Any, Dict

# Base directory for resources – can be overridden by environment variable
RESOURCE_ROOT = os.getenv(
    "CONTEXT_ENGINE_RESOURCES_ROOT",
    os.path.join(os.path.dirname(__file__), "..", "resources"),
)

# Simple in‑memory cache
_CACHE: Dict[str, Any] = {}


def _load_yaml(relative_path: str) -> Any:
    """Load a YAML file from the resources directory.

    The result is cached after the first load.
    """
    absolute_path = os.path.abspath(os.path.join(RESOURCE_ROOT, relative_path))
    if absolute_path in _CACHE:
        return _CACHE[absolute_path]
    if not os.path.isfile(absolute_path):
        raise FileNotFoundError(f"Resource file not found: {absolute_path}")
    with open(absolute_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    _CACHE[absolute_path] = data
    return data


def get_normativa(id: str) -> Dict[str, Any]:
    """Return the normativa resource identified by ``id``.

    Expected file layout: ``normativas/<id>.yaml``
    """
    return _load_yaml(os.path.join("normativas", f"{id}.yaml"))


def get_taxonomia(id: str) -> Dict[str, Any]:
    """Return the taxonomia resource identified by ``id``.

    Expected file layout: ``taxonomias/<id>.yaml``
    """
    return _load_yaml(os.path.join("taxonomias", f"{id}.yaml"))


def get_template(id: str) -> Dict[str, Any]:
    """Return the template resource identified by ``id``.

    Expected file layout: ``templates/<id>.yaml``
    """
    return _load_yaml(os.path.join("templates", f"{id}.yaml"))
