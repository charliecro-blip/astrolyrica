#!/usr/bin/env python3
"""Assemble a manual AstroLyrica experiment prompt from YAML data."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
DEFAULT_INPUT = REPO_ROOT / "experiments" / "moon_scorpio_5th_input.yaml"
DEFAULT_OUTPUT = REPO_ROOT / "outputs" / "experiments" / "moon_scorpio_5th_prompt.md"
TEMPLATE_PATH = REPO_ROOT / "prompts" / "generation_prompt.md"

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


def load_yaml(path: Path) -> Any:
    """Load a YAML document from disk."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except FileNotFoundError as exc:
        raise ValueError(f"Required file not found: {path.relative_to(REPO_ROOT)}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Could not parse YAML file {path.relative_to(REPO_ROOT)}: {exc}") from exc


def load_data_directory() -> dict[str, Any]:
    """Load all YAML files in data/ keyed by filename."""
    data: dict[str, Any] = {}
    for yaml_file in sorted(DATA_DIR.glob("*.yaml")):
        data[yaml_file.name] = load_yaml(yaml_file)
    if not data:
        raise ValueError(f"No YAML files found in {DATA_DIR.relative_to(REPO_ROOT)}")
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


def load_optional_commonplace_images(data: dict[str, Any]) -> Any:
    """Return commonplace image data when the optional file is present."""
    return data.get("commonplace_images.yaml", {})


def assemble_prompt(
    experiment: dict[str, Any],
    entries: dict[str, dict[str, Any]],
    template: str,
    commonplace_images: Any | None = None,
) -> str:
    """Replace template placeholders with experiment material."""
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
        "{{VOICE}}": dump_block(entries["voice"]),
        "{{FORM}}": dump_block(entries["form"]),
        "{{SLIDERS}}": dump_block(experiment.get("sliders", {})),
        "{{COMMONPLACE_IMAGES}}": dump_block(commonplace_images or {}),
    }

    prompt = template
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)
    return prompt


def main(argv: list[str]) -> int:
    input_path = Path(argv[1]) if len(argv) > 1 else DEFAULT_INPUT
    output_path = Path(argv[2]) if len(argv) > 2 else DEFAULT_OUTPUT
    if not input_path.is_absolute():
        input_path = REPO_ROOT / input_path
    if not output_path.is_absolute():
        output_path = REPO_ROOT / output_path

    try:
        data = load_data_directory()
        experiment = load_yaml(input_path)
        if not isinstance(experiment, dict):
            raise ValueError("Experiment input must be a YAML mapping")

        entries = {
            kind: find_entry(data, kind, resolve_id(kind, experiment.get(kind)))
            for kind in DATA_KEYS
        }

        template = TEMPLATE_PATH.read_text(encoding="utf-8")
        commonplace_images = load_optional_commonplace_images(data)
        prompt = assemble_prompt(experiment, entries, template, commonplace_images)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(prompt, encoding="utf-8")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(output_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
