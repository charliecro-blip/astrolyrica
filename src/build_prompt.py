#!/usr/bin/env python3
"""Assemble AstroLyrica experiment prompts from YAML data."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
OUTPUTS_DIR = REPO_ROOT / "outputs" / "experiments"
DEFAULT_INPUT = EXPERIMENTS_DIR / "moon_scorpio_5th_input.yaml"
DEFAULT_OUTPUT = OUTPUTS_DIR / "moon_scorpio_5th_prompt.md"
DEFAULT_SUMMARY = OUTPUTS_DIR / "batch_summary.md"
TEMPLATE_PATH = REPO_ROOT / "prompts" / "generation_prompt.md"
COMBINATIONS_FILENAME = "combinations.yaml"
DEFAULT_OUTPUT_REQUESTS = [
    "Plain-English meaning brief",
    "X-length poem",
    "Five-line oracle",
    "Daily horoscope paragraph",
    "Image prompt",
]

EXPERIMENT_CONTROL_FIELDS = (
    "intent",
    "audience",
    "occasion",
    "variation_seed",
    "emphasize",
    "avoid",
    "outputs",
    "notes",
)

OUTPUT_LABELS = {
    "meaning_brief": "Plain-English meaning brief",
    "x_length_poem": "X-length poem",
    "five_line_oracle": "Five-line oracle",
    "daily_horoscope": "Daily horoscope paragraph",
    "image_prompt": "Image prompt",
}

DATA_KEYS = {
    "planet": ("planets.yaml", "planets"),
    "sign": ("signs.yaml", "signs"),
    "house": ("houses.yaml", "houses"),
    "voice": ("voices.yaml", "voices"),
    "form": ("forms.yaml", "forms"),
}

HOUSE_ALIASES = {
    "first": "first_house",
    "second": "second_house",
    "third": "third_house",
    "fourth": "fourth_house",
    "fifth": "fifth_house",
    "sixth": "sixth_house",
    "seventh": "seventh_house",
    "eighth": "eighth_house",
    "ninth": "ninth_house",
    "tenth": "tenth_house",
    "eleventh": "eleventh_house",
    "twelfth": "twelfth_house",
}

HOUSE_NUMBER_ALIASES = {
    "first_house": "1st_house",
    "second_house": "2nd_house",
    "third_house": "3rd_house",
    "fourth_house": "4th_house",
    "fifth_house": "5th_house",
    "sixth_house": "6th_house",
    "seventh_house": "7th_house",
    "eighth_house": "8th_house",
    "ninth_house": "9th_house",
    "tenth_house": "10th_house",
    "eleventh_house": "11th_house",
    "twelfth_house": "12th_house",
}


def repo_path(path: Path) -> str:
    """Return a display path relative to the repo when possible."""
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def resolve_repo_path(path: str | Path) -> Path:
    """Resolve a user-provided path relative to the repository root."""
    candidate = Path(path)
    return candidate if candidate.is_absolute() else REPO_ROOT / candidate


def load_yaml(path: Path) -> Any:
    """Load a YAML document from disk."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"Required file not found: {repo_path(path)}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Could not parse YAML file {repo_path(path)}: {exc}") from exc


def load_data_directory() -> dict[str, Any]:
    """Load all YAML files in data/ keyed by filename."""
    data: dict[str, Any] = {}
    for yaml_file in sorted(DATA_DIR.glob("*.yaml")):
        data[yaml_file.name] = load_yaml(yaml_file)
    if not data:
        raise ValueError(f"No YAML files found in {repo_path(DATA_DIR)}")
    return data


def resolve_id(kind: str, raw_id: Any) -> str:
    """Return the data id to look up, including friendly house aliases."""
    if not isinstance(raw_id, str) or not raw_id.strip():
        raise ValueError(f"Experiment field '{kind}' must be a non-empty string")
    item_id = raw_id.strip()
    if kind == "house":
        return HOUSE_ALIASES.get(item_id, item_id)
    return item_id


def find_entry(data: dict[str, Any], kind: str, item_id: str) -> dict[str, Any]:
    """Find a data entry by id or fail with a clear error."""
    filename, collection_key = DATA_KEYS[kind]
    collection = data.get(filename, {}).get(collection_key, [])
    for entry in collection:
        if isinstance(entry, dict) and entry.get("id") == item_id:
            return entry

    available = ", ".join(
        entry.get("id", "<missing id>") for entry in collection if isinstance(entry, dict)
    )
    raise ValueError(
        f"Missing {kind} id '{item_id}' in data/{filename}. Available ids: {available}"
    )


def dump_block(value: Any) -> str:
    """Render structured values as readable YAML blocks."""
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True).strip()


def house_id_variants(house_id: str) -> list[str]:
    """Return supported text variants for a normalized house id."""
    variants = [house_id]
    if house_id.endswith("_house"):
        variants.append(house_id.removesuffix("_house"))
    numbered = HOUSE_NUMBER_ALIASES.get(house_id)
    if numbered:
        variants.append(numbered)
    return list(dict.fromkeys(variants))


def candidate_combination_ids(planet_id: str, sign_id: str, house_id: str) -> list[str]:
    """Return combination ids relevant to the selected planet, sign, and house."""
    house_variants = house_id_variants(house_id)
    candidates = [f"{planet_id}_in_{sign_id}"]
    for template in (
        f"{planet_id}_in_{{house}}",
        f"{sign_id}_{{house}}",
        f"{planet_id}_in_{sign_id}_{{house}}",
    ):
        candidates.extend(template.format(house=variant) for variant in house_variants)
    return list(dict.fromkeys(candidates))


def normalize_combination_entries(raw_combinations: Any) -> list[dict[str, Any]]:
    """Normalize supported combinations.yaml shapes into id-bearing mappings."""
    if not raw_combinations:
        return []
    if isinstance(raw_combinations, dict):
        raw_entries = raw_combinations.get("combinations", raw_combinations)
        if isinstance(raw_entries, dict):
            return [
                {"id": entry_id, **entry}
                if isinstance(entry, dict)
                else {"id": entry_id, "notes": entry}
                for entry_id, entry in raw_entries.items()
            ]
        raw_combinations = raw_entries
    if isinstance(raw_combinations, list):
        return [
            entry
            for entry in raw_combinations
            if isinstance(entry, dict) and entry.get("id")
        ]
    return []


def find_combination_notes(
    data: dict[str, Any], entries: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    """Find optional combination notes for the selected planet, sign, and house."""
    combinations = normalize_combination_entries(data.get(COMBINATIONS_FILENAME))
    candidate_ids = set(
        candidate_combination_ids(
            entries["planet"]["id"], entries["sign"]["id"], entries["house"]["id"]
        )
    )
    return [entry for entry in combinations if entry.get("id") in candidate_ids]


def render_combination_notes(notes: list[dict[str, Any]], enabled: bool) -> str:
    """Render matching combination notes for the prompt."""
    if not enabled:
        return "Combination notes disabled for this experiment."
    if not notes:
        return "No specific combination notes found."
    return dump_block({"combinations": notes})


def load_optional_commonplace_images(data: dict[str, Any]) -> Any:
    """Return commonplace image data when the optional file is present."""
    return data.get("commonplace_images.yaml", {})


def normalize_controls(experiment: dict[str, Any]) -> dict[str, Any]:
    """Return validated experiment controls with defaults."""
    raw_controls = experiment.get("controls", {})
    if raw_controls is None:
        raw_controls = {}
    if not isinstance(raw_controls, dict):
        raise ValueError("Experiment field 'controls' must be a mapping when present")

    include_sections = raw_controls.get("include_sections", {})
    if include_sections is None:
        include_sections = {}
    if not isinstance(include_sections, dict):
        raise ValueError("Experiment controls.include_sections must be a mapping")

    outputs = experiment.get("outputs", raw_controls.get("outputs", DEFAULT_OUTPUT_REQUESTS))
    if outputs is None:
        outputs = DEFAULT_OUTPUT_REQUESTS
    if not isinstance(outputs, list) or not all(
        isinstance(output, str) and output.strip() for output in outputs
    ):
        raise ValueError("Experiment outputs must be a list of non-empty strings")

    return {
        "include_sections": {
            "combination_notes": bool(include_sections.get("combination_notes", True)),
            "commonplace_images": bool(include_sections.get("commonplace_images", True)),
            "sliders": bool(include_sections.get("sliders", True)),
        },
        "outputs": [output.strip() for output in outputs],
        "notes": experiment.get("notes", raw_controls.get("notes", "")),
    }


def display_output(output: str) -> str:
    """Return the human-readable label for an output key."""
    if output in DEFAULT_OUTPUT_REQUESTS:
        return output
    return OUTPUT_LABELS.get(output, output.replace("_", " ").strip().title())


def render_outputs(outputs: list[str]) -> str:
    """Render requested generation outputs as a numbered Markdown list."""
    return "\n".join(
        f"{index}. {display_output(output)}" for index, output in enumerate(outputs, 1)
    )


def render_experiment_controls(experiment: dict[str, Any]) -> str:
    """Render optional experiment controls for the generation prompt."""
    controls: dict[str, Any] = {}
    for field in EXPERIMENT_CONTROL_FIELDS:
        if field in experiment and experiment[field] not in (None, "", []):
            value = experiment[field]
            if field == "outputs":
                if not isinstance(value, list) or not all(
                    isinstance(item, str) and item.strip() for item in value
                ):
                    raise ValueError("Experiment outputs must be a list of non-empty strings")
                controls[field] = [display_output(item.strip()) for item in value]
            else:
                controls[field] = value

    if not controls:
        return "No additional experiment controls provided."
    return dump_block(controls)


def assemble_prompt(
    experiment: dict[str, Any],
    entries: dict[str, dict[str, Any]],
    template: str,
    commonplace_images: Any | None = None,
    combination_notes: list[dict[str, Any]] | None = None,
) -> str:
    """Replace template placeholders with experiment material."""
    controls = normalize_controls(experiment)
    include_sections = controls["include_sections"]
    astrology_context = "\n".join(
        [
            f"- Planet: {entries['planet']['name']} ({entries['planet']['id']})",
            f"- Sign: {entries['sign']['name']} ({entries['sign']['id']})",
            f"- House: {entries['house']['name']} ({entries['house']['id']})",
        ]
    )
    symbolic_material = dump_block(
        {
            "planet": entries["planet"],
            "sign": entries["sign"],
            "house": entries["house"],
        }
    )
    replacements = {
        "{{ASTROLOGY_CONTEXT}}": astrology_context,
        "{{SYMBOLIC_MATERIAL}}": symbolic_material,
        "{{COMBINATION_NOTES}}": render_combination_notes(
            combination_notes or [], include_sections["combination_notes"]
        ),
        "{{VOICE}}": dump_block(entries["voice"]),
        "{{FORM}}": dump_block(entries["form"]),
        "{{SLIDERS}}": dump_block(experiment.get("sliders", {}))
        if include_sections["sliders"]
        else "Sliders disabled for this experiment.",
        "{{EXPERIMENT_CONTROLS}}": render_experiment_controls(experiment),
        "{{COMMONPLACE_IMAGES}}": dump_block(commonplace_images or {})
        if include_sections["commonplace_images"]
        else "Commonplace image guardrails disabled for this experiment.",
        "{{REQUESTED_OUTPUTS}}": render_outputs(controls["outputs"]),
    }

    prompt = template
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)
    return prompt


def default_output_for_input(input_path: Path, output_dir: Path = OUTPUTS_DIR) -> Path:
    """Return the conventional prompt output path for an experiment input."""
    stem = input_path.stem
    if stem.endswith("_input"):
        stem = stem[: -len("_input")]
    return output_dir / f"{stem}_prompt.md"


def build_one(
    data: dict[str, Any], template: str, input_path: Path, output_path: Path
) -> dict[str, str]:
    """Build one prompt and return summary information."""
    experiment = load_yaml(input_path)
    if not isinstance(experiment, dict):
        raise ValueError(f"Experiment input must be a YAML mapping: {repo_path(input_path)}")

    entries = {
        kind: find_entry(data, kind, resolve_id(kind, experiment.get(kind)))
        for kind in DATA_KEYS
    }
    commonplace_images = load_optional_commonplace_images(data)
    combination_notes = find_combination_notes(data, entries)
    prompt = assemble_prompt(
        experiment, entries, template, commonplace_images, combination_notes
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt, encoding="utf-8")
    return {
        "input": repo_path(input_path),
        "output": repo_path(output_path),
        "context": (
            f"{entries['planet']['name']} in {entries['sign']['name']} "
            f"in {entries['house']['name']}"
        ),
    }


def discover_experiments(experiments_dir: Path) -> list[Path]:
    """Return batchable experiment YAML files from a directory."""
    return sorted(experiments_dir.glob("*.yaml"))


def write_batch_summary(rows: list[dict[str, str]], summary_path: Path) -> None:
    """Write a small Markdown summary for batch generation."""
    lines = ["# AstroLyrica Batch Prompt Summary", ""]
    if not rows:
        lines.append("No experiment input files found.")
    else:
        lines.extend(["| Experiment | Context | Prompt |", "| --- | --- | --- |"])
        for row in rows:
            lines.append(f"| `{row['input']}` | {row['context']} | `{row['output']}` |")
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
