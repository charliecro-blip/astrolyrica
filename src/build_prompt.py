#!/usr/bin/env python3
"""Assemble AstroLyrica experiment prompts from YAML data."""

from __future__ import annotations

import argparse
import sys

from prompt_engine import (
    DEFAULT_INPUT,
    DEFAULT_OUTPUT,
    DEFAULT_SUMMARY,
    EXPERIMENTS_DIR,
    OUTPUTS_DIR,
    TEMPLATE_PATH,
    build_one,
    default_output_for_input,
    discover_experiments,
    load_data_directory,
    repo_path,
    resolve_repo_path,
    write_batch_summary,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments while preserving the original positional workflow."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", help="Experiment YAML input path")
    parser.add_argument("output", nargs="?", help="Markdown prompt output path")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Build every *_input.yaml file in the experiments directory",
    )
    parser.add_argument(
        "--experiments-dir",
        default=str(EXPERIMENTS_DIR),
        help="Directory to search when using --batch",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUTS_DIR),
        help="Directory for conventional batch prompt outputs",
    )
    parser.add_argument(
        "--summary",
        default=str(DEFAULT_SUMMARY),
        help="Markdown summary path for --batch runs",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        data = load_data_directory()
        template = TEMPLATE_PATH.read_text(encoding="utf-8")

        if args.batch:
            experiments_dir = resolve_repo_path(args.experiments_dir)
            output_dir = resolve_repo_path(args.output_dir)
            summary_path = resolve_repo_path(args.summary)
            input_paths = discover_experiments(experiments_dir)
            rows = [
                build_one(
                    data,
                    template,
                    input_path,
                    default_output_for_input(input_path, output_dir),
                )
                for input_path in input_paths
            ]
            write_batch_summary(rows, summary_path)
            for row in rows:
                print(row["output"])
            print(repo_path(summary_path))
            return 0

        input_path = resolve_repo_path(args.input) if args.input else DEFAULT_INPUT
        output_path = resolve_repo_path(args.output) if args.output else DEFAULT_OUTPUT
        row = build_one(data, template, input_path, output_path)
        print(row["output"])
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
