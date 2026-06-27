#!/usr/bin/env python3
"""Build a manual experiment prompt from local YAML data files."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TEMPLATE_PATH = ROOT / "prompts" / "generation_prompt.md"
DEFAULT_INPUT = ROOT / "experiments" / "moon_scorpio_5th_input.yaml"
DEFAULT_OUTPUT = ROOT / "outputs" / "experiments" / "moon_scorpio_5th_prompt.md"


class PromptBuildError(Exception):
    """Raised when the prompt cannot be assembled cleanly."""


def parse_scalar(value):
    value = value.strip()
    if value == "":
        return ""
    if value.isdigit():
        return int(value)
    return value


def load_simple_yaml(path):
    """Load the small mapping-style YAML files used by these experiments."""
    if not path.exists():
        raise PromptBuildError(f"Missing YAML file: {path}")

    root = {}
    current_mapping = None

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if ":" not in raw_line:
            raise PromptBuildError(f"Invalid YAML at {path}:{line_number}: {raw_line}")
        key, value = raw_line.strip().split(":", 1)
        if indent == 0:
            if value.strip() == "":
                root[key] = {}
                current_mapping = root[key]
            else:
                root[key] = parse_scalar(value)
                current_mapping = None
        elif indent == 2 and current_mapping is not None:
            current_mapping[key] = parse_scalar(value)
        else:
            raise PromptBuildError(f"Unsupported YAML shape at {path}:{line_number}: {raw_line}")

    return root


def load_entry(kind, key):
    path = DATA_DIR / kind / f"{key}.yaml"
    entry = load_simple_yaml(path)
    if entry.get("key") != key:
        raise PromptBuildError(f"Expected key '{key}' in {path}, found '{entry.get('key')}'")
    return entry


def format_entry(entry):
    parts = [f"- Name: {entry.get('name', entry['key'])}"]
    if entry.get("keywords"):
        parts.append(f"- Keywords: {entry['keywords']}")
    if entry.get("prompt_text"):
        parts.append(f"- Prompt text: {entry['prompt_text']}")
    return "\n".join(parts)


def format_sliders(sliders):
    return "\n".join(f"- {name}: {value}/10" for name, value in sliders.items())


def build_prompt(input_path=DEFAULT_INPUT):
    experiment = load_simple_yaml(input_path)
    required = ["planet", "sign", "house", "voice", "form", "sliders"]
    missing = [field for field in required if field not in experiment]
    if missing:
        raise PromptBuildError(f"Missing required experiment fields: {', '.join(missing)}")

    replacements = {
        "{{planet}}": format_entry(load_entry("planets", experiment["planet"])),
        "{{sign}}": format_entry(load_entry("signs", experiment["sign"])),
        "{{house}}": format_entry(load_entry("houses", experiment["house"])),
        "{{voice}}": format_entry(load_entry("voices", experiment["voice"])),
        "{{form}}": format_entry(load_entry("forms", experiment["form"])),
        "{{sliders}}": format_sliders(experiment["sliders"]),
    }

    prompt = TEMPLATE_PATH.read_text(encoding="utf-8")
    for placeholder, value in replacements.items():
        prompt = prompt.replace(placeholder, value)
    return prompt.rstrip() + "\n"


def main():
    input_path = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_INPUT
    output_path = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else DEFAULT_OUTPUT
    prompt = build_prompt(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(prompt, encoding="utf-8")
    print(f"Wrote prompt to {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
