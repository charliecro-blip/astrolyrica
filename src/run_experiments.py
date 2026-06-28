#!/usr/bin/env python3
"""Build prompts for every AstroLyrica experiment input."""

from __future__ import annotations

import sys

from build_prompt import (
    DEFAULT_SUMMARY,
    EXPERIMENTS_DIR,
    OUTPUTS_DIR,
    TEMPLATE_PATH,
    build_one,
    default_output_for_input,
    discover_experiments,
    load_data_directory,
    repo_path,
    write_batch_summary,
)


def main() -> int:
    """Discover experiment YAML files and write prompt outputs."""
    try:
        data = load_data_directory()
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
        input_paths = discover_experiments(EXPERIMENTS_DIR)
        if not input_paths:
            print(f"No experiment YAML files found in {repo_path(EXPERIMENTS_DIR)}")
            write_batch_summary([], DEFAULT_SUMMARY)
            return 0

        rows = []
        for input_path in input_paths:
            try:
                rows.append(
                    build_one(
                        data,
                        template,
                        input_path,
                        default_output_for_input(input_path, OUTPUTS_DIR),
                    )
                )
            except ValueError as exc:
                raise ValueError(f"Malformed experiment {repo_path(input_path)}: {exc}") from exc

        write_batch_summary(rows, DEFAULT_SUMMARY)
        print("Generated experiment prompts:")
        for row in rows:
            print(f"- {row['output']}")
        print(f"Summary: {repo_path(DEFAULT_SUMMARY)}")
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
