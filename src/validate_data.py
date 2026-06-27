#!/usr/bin/env python3
"""Validate that AstroLyrica YAML data files parse successfully."""

from __future__ import annotations

from pathlib import Path
import sys

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"


def validate_yaml_files() -> int:
    """Load every YAML file in data/ and report parse status."""
    yaml_files = sorted(DATA_DIR.glob("*.yaml"))
    if not yaml_files:
        print(f"No YAML files found in {DATA_DIR}", file=sys.stderr)
        return 1

    failures: list[tuple[Path, Exception]] = []
    for yaml_file in yaml_files:
        try:
            with yaml_file.open("r", encoding="utf-8") as handle:
                yaml.safe_load(handle)
            print(f"OK: {yaml_file.relative_to(REPO_ROOT)}")
        except yaml.YAMLError as exc:
            failures.append((yaml_file, exc))

    if failures:
        print("\nYAML validation failed:", file=sys.stderr)
        for yaml_file, exc in failures:
            print(f"- {yaml_file.relative_to(REPO_ROOT)}: {exc}", file=sys.stderr)
        return 1

    print(f"\nValidated {len(yaml_files)} YAML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate_yaml_files())
