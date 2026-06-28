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
COMBINATIONS_FILENAME = "combinations.yaml"

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
    """Return combination ids relevant to the selected planet, sign, and house.

    Keep the high-level combination order stable while allowing house id aliases
    such as ``fifth_house`` to match numbered data ids such as ``5th_house``.
    """
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


def render_combination_notes(notes: list[dict[str, Any]]) -> str:
    """Render matching combination notes for the prompt."""
    if not notes:
        return "No specific combination notes found."
    return dump_block({"combinations": notes})


def load_optional_commonplace_images(data: dict[str, Any]) -> Any:
    """Return commonplace image data when the optional file is present."""
    return data.get("commonplace_images.yaml", {})


def assemble_prompt(
    experiment: dict[str, Any],
    entries: dict[str, dict[str, Any]],
    template: str,
    commonplace_images: Any | None = None,
    combination_notes: list[dict[str, Any]] | None = None,
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
        "{{COMBINATION_NOTES}}": render_combination_notes(combination_notes or []),
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
        combination_notes = find_combination_notes(data, entries)
        prompt = assemble_prompt(
            experiment, entries, template, commonplace_images, combination_notes
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(prompt, encoding="utf-8")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(output_path.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
