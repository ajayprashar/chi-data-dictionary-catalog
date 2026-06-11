"""PBIP and demo path constants.

Power BI OPC packaging (Publish / Save as PBIX) validates relative URIs inside
the project archive. Path segments and packaged part filenames must be
**alphanumeric only** (no spaces, hyphens, or underscores).

Applies to:
  - repo extract folder under C:\\AI\\
  - .pbip / .Report / .SemanticModel directory names
  - theme and other StaticResources filenames referenced in report.json

Parquet *filenames* at repo root (ddc-*.parquet) are unchanged.
"""

from __future__ import annotations

import re
from pathlib import Path

# Alphanumeric only for OPC-safe directory and packaged-file names.
PBIP_PROJECT = "chiddc"
DEMO_ROOT_NAME = "chiddc"

REPO_PARQUET = rf"C:\AI\{DEMO_ROOT_NAME}"

PBIP_FILE = f"{PBIP_PROJECT}.pbip"
PBIP_REPORT_DIR = f"{PBIP_PROJECT}.Report"
PBIP_SEMANTIC_MODEL_DIR = f"{PBIP_PROJECT}.SemanticModel"

# Portable package zip: alphanumeric only (no hyphens), e.g. chiddc20260611.zip
PACKAGE_ZIP_STEM = DEMO_ROOT_NAME

# Theme label (in-report display) vs OPC-safe filename (no spaces).
THEME_LABEL = "CHI High Contrast"
THEME_FILE = "CHIHighContrast.json"
THEME_RESOURCE_PATH = f"BaseThemes/{THEME_FILE}"

_OPC_UNSAFE = re.compile(r"[^A-Za-z0-9]")


def assert_opc_safe_segment(name: str, *, context: str = "") -> None:
    """Raise if a path segment or packaged filename is not alphanumeric."""
    if _OPC_UNSAFE.search(name):
        raise ValueError(f"OPC-unsafe path segment {name!r}{f' ({context})' if context else ''}")


def pbip_root(repo: Path) -> Path:
    return repo / "workbooks" / "pbip"


def report_definition(repo: Path) -> Path:
    return pbip_root(repo) / PBIP_REPORT_DIR / "definition"


def semantic_model_definition(repo: Path) -> Path:
    return pbip_root(repo) / PBIP_SEMANTIC_MODEL_DIR / "definition"


def theme_dir(repo: Path) -> Path:
    return (
        pbip_root(repo)
        / PBIP_REPORT_DIR
        / "StaticResources"
        / "SharedResources"
        / "BaseThemes"
    )
