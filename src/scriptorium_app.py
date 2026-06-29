#!/usr/bin/env python3
"""Local Scriptorium UI for editing and previewing AstroLyrica experiment prompts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from flask import Flask, abort, render_template_string, request, url_for

from prompt_engine import (
    DATA_KEYS,
    EXPERIMENTS_DIR,
    OUTPUTS_DIR,
    TEMPLATE_PATH,
    assemble_experiment_prompt,
    build_one,
    default_output_for_input,
    discover_experiments,
    load_data_directory,
    load_yaml,
    repo_path,
    resolve_id,
)

app = Flask(__name__)

COMMON_SLIDERS = (
    "imagery",
    "surrealism",
    "embodiment",
    "technical_astrology",
    "darkness",
    "instruction",
)
REQUIRED_FIELDS = ("planet", "sign", "house", "voice", "form")
OPTIONAL_TEXT_FIELDS = ("intent", "audience", "occasion", "variation_seed")
LIST_TEXTAREA_FIELDS = ("emphasize", "avoid", "outputs", "notes")
SAFE_STEM_RE = re.compile(r"[^a-zA-Z0-9_-]+")

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AstroLyrica Scriptorium</title>
  <style>
    :root { color-scheme: light; }
    body { margin: 0; background: #f4efe6; color: #2f251c; font-family: Georgia, "Times New Roman", serif; line-height: 1.5; }
    main { max-width: 1220px; margin: 0 auto; padding: 3rem 1.5rem 4rem; }
    header { border-bottom: 1px solid #d7cbbb; margin-bottom: 1.5rem; padding-bottom: 1rem; }
    h1 { font-size: clamp(2rem, 4vw, 3.5rem); margin: 0; font-weight: 500; letter-spacing: .02em; }
    h2 { margin: 0 0 .75rem; font-weight: 500; }
    .subtitle, .help { color: #6c5b4a; }
    .desk { display: grid; grid-template-columns: minmax(320px, 420px) 1fr; gap: 1.25rem; align-items: start; }
    .panel { background: #fffaf1; border: 1px solid #d8c9b4; border-radius: 14px; box-shadow: 0 12px 40px rgba(77, 56, 35, .08); padding: 1rem; }
    label, .label { display: block; color: #6a4d34; font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; }
    input, select, textarea { box-sizing: border-box; width: 100%; margin-top: .35rem; padding: .65rem; border: 1px solid #c7b59d; border-radius: 10px; background: #fffdf8; color: #2f251c; font: inherit; }
    textarea { min-height: 5.5rem; resize: vertical; }
    textarea.prompt { min-height: 74vh; font: 0.92rem/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; white-space: pre; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: .85rem; }
    .field { margin-bottom: .85rem; }
    .slider-row { display: grid; grid-template-columns: 1fr 6rem; gap: .65rem; align-items: end; margin-bottom: .6rem; }
    .actions { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 1rem; }
    button { border: 0; border-radius: 999px; padding: .72rem 1rem; background: #704214; color: #fffaf1; font: inherit; cursor: pointer; }
    button.secondary { background: #8b735b; }
    .checkbox { display: flex; gap: .5rem; align-items: center; color: #5e4a38; }
    .checkbox input { width: auto; margin: 0; }
    .message { margin-bottom: 1rem; padding: .75rem; border-radius: 10px; background: #eef6e8; border: 1px solid #bdd0ad; }
    .error { background: #fae8df; border-color: #d9a991; }
    .empty { padding: 2rem; color: #6c5b4a; }
    a { color: #704214; }
    @media (max-width: 860px) { .desk, .grid { grid-template-columns: 1fr; } main { padding-top: 1.5rem; } }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Scriptorium</h1>
      <p class="subtitle">A local workbench for editing experiment controls, previewing assembled prompts, and saving new YAML variants.</p>
    </header>
    {% if message %}<div class="message">{{ message }}</div>{% endif %}
    {% if error %}<div class="message error">{{ error }}</div>{% endif %}
    <section class="desk">
      <aside class="panel">
        <form method="get" action="/">
          <label for="experiment">Experiment</label>
          <select id="experiment" name="experiment" onchange="if (this.value) window.location.href=this.value;">
            <option value="{{ url_for('index') }}">Choose an experiment…</option>
            {% for experiment in experiments %}
              <option value="{{ url_for('experiment_preview', experiment_name=experiment.name) }}" {% if selected == experiment.name %}selected{% endif %}>{{ experiment.name }}</option>
            {% endfor %}
          </select>
        </form>

        {% if experiment_data %}
        <form method="post" action="{{ url_for('experiment_preview', experiment_name=selected) if selected else url_for('index') }}">
          <h2>Controls</h2>
          <div class="grid">
            {% for field in required_fields %}
            <div class="field">
              <label for="{{ field }}">{{ field }}</label>
              <select id="{{ field }}" name="{{ field }}" required>
                {% for option in choices[field] %}
                  <option value="{{ option.id }}" {% if experiment_data.get(field) == option.id or resolved.get(field) == option.id %}selected{% endif %}>{{ option.name }} ({{ option.id }})</option>
                {% endfor %}
              </select>
            </div>
            {% endfor %}
          </div>
          {% for field in optional_text_fields %}
          <div class="field"><label for="{{ field }}">{{ field }}</label><input id="{{ field }}" name="{{ field }}" value="{{ experiment_data.get(field, '') }}"></div>
          {% endfor %}
          {% for field in list_textarea_fields %}
          <div class="field"><label for="{{ field }}">{{ field }} <span class="help">(one item per line)</span></label><textarea id="{{ field }}" name="{{ field }}">{{ list_values.get(field, '') }}</textarea></div>
          {% endfor %}
          <div class="field">
            <span class="label">sliders</span>
            {% for name in slider_names %}
              <div class="slider-row"><label for="slider_{{ name }}">{{ name.replace('_', ' ') }}</label><input id="slider_{{ name }}" name="slider_{{ name }}" type="number" min="0" max="10" step="1" value="{{ sliders.get(name, 0) }}"></div>
            {% endfor %}
          </div>
          <div class="field"><label for="filename_stem">safe filename stem</label><input id="filename_stem" name="filename_stem" value="{{ filename_stem }}" placeholder="venus_taurus_7th_variant_1"></div>
          <label class="checkbox"><input type="checkbox" name="overwrite" value="1"> Overwrite existing YAML and prompt if present</label>
          <div class="actions">
            <button type="submit" name="action" value="preview">Preview prompt</button>
            <button class="secondary" type="submit" name="action" value="save">Save as new experiment</button>
          </div>
        </form>
        {% else %}
          <div class="empty">Select an experiment to begin editing. Preview does not overwrite the source YAML.</div>
        {% endif %}
      </aside>
      <section class="panel">
        {% if prompt %}
          <div class="label">Generated prompt preview</div>
          <textarea class="prompt" readonly spellcheck="false">{{ prompt }}</textarea>
        {% else %}
          <div class="empty">The assembled prompt will appear here. This local interface does not call an LLM.</div>
        {% endif %}
      </section>
    </section>
  </main>
</body>
</html>
"""


def experiment_paths() -> dict[str, Path]:
    """Return route-safe experiment file names mapped to paths."""
    return {path.name: path for path in discover_experiments(EXPERIMENTS_DIR)}


def choices_from_data(data: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    """Build dropdown choices from existing YAML data."""
    choices: dict[str, list[dict[str, str]]] = {}
    for kind, (filename, collection_key) in DATA_KEYS.items():
        rows = data.get(filename, {}).get(collection_key, [])
        choices[kind] = [
            {"id": row.get("id", ""), "name": row.get("name", row.get("id", ""))}
            for row in rows
            if isinstance(row, dict) and row.get("id")
        ]
    return choices


def textarea_to_list(value: str) -> list[str]:
    """Treat each non-empty textarea line as one list item."""
    return [line.strip() for line in value.splitlines() if line.strip()]


def value_to_textarea(value: Any) -> str:
    """Render a scalar or list value into one-item-per-line textarea text."""
    if isinstance(value, list):
        return "\n".join(str(item) for item in value if str(item).strip())
    if value in (None, ""):
        return ""
    return str(value)


def sanitize_filename_stem(raw_stem: str) -> str:
    """Return a safe experiments/ filename stem without path traversal."""
    stem = SAFE_STEM_RE.sub("_", raw_stem.strip()).strip("._-").lower()
    if stem.endswith("_input"):
        stem = stem[: -len("_input")]
    if not stem or stem in {".", ".."}:
        raise ValueError("Filename stem must contain at least one letter or number")
    return stem


def experiment_from_form() -> dict[str, Any]:
    """Convert submitted form fields into an experiment mapping."""
    experiment: dict[str, Any] = {}
    for field in REQUIRED_FIELDS + OPTIONAL_TEXT_FIELDS:
        value = request.form.get(field, "").strip()
        if value or field in REQUIRED_FIELDS:
            experiment[field] = value
    for field in LIST_TEXTAREA_FIELDS:
        values = textarea_to_list(request.form.get(field, ""))
        if values:
            experiment[field] = values
    sliders: dict[str, int] = {}
    for name in COMMON_SLIDERS:
        raw_value = request.form.get(f"slider_{name}", "").strip()
        if raw_value:
            sliders[name] = max(0, min(10, int(raw_value)))
    if sliders:
        experiment["sliders"] = sliders
    return experiment


def default_filename_stem(experiment: dict[str, Any]) -> str:
    """Suggest a conventional, editable filename stem."""
    parts = [str(experiment.get(field, "")).replace("_house", "") for field in ("planet", "sign", "house")]
    return sanitize_filename_stem("_".join(part for part in parts if part) or "experiment_variant")


def render_page(selected: str | None = None, experiment_data: dict[str, Any] | None = None, prompt: str = "", message: str = "", error: str = "") -> str:
    """Render the shared Scriptorium page."""
    data = load_data_directory()
    experiment_data = experiment_data or {}
    resolved = {}
    for kind in REQUIRED_FIELDS:
        try:
            resolved[kind] = resolve_id(kind, experiment_data.get(kind))
        except ValueError:
            resolved[kind] = experiment_data.get(kind, "")
    sliders = {name: int(experiment_data.get("sliders", {}).get(name, 0)) for name in COMMON_SLIDERS}
    return render_template_string(
        PAGE_TEMPLATE,
        experiments=[{"name": name} for name in experiment_paths()],
        selected=selected,
        choices=choices_from_data(data),
        required_fields=REQUIRED_FIELDS,
        optional_text_fields=OPTIONAL_TEXT_FIELDS,
        list_textarea_fields=LIST_TEXTAREA_FIELDS,
        list_values={field: value_to_textarea(experiment_data.get(field, "")) for field in LIST_TEXTAREA_FIELDS},
        slider_names=COMMON_SLIDERS,
        sliders=sliders,
        resolved=resolved,
        filename_stem=request.form.get("filename_stem", default_filename_stem(experiment_data)) if experiment_data else "",
        experiment_data=experiment_data,
        prompt=prompt,
        message=message,
        error=error,
    )


def prompt_for_experiment(experiment: dict[str, Any]) -> str:
    """Assemble a prompt from an in-memory experiment mapping."""
    return assemble_experiment_prompt(experiment, load_data_directory(), TEMPLATE_PATH.read_text(encoding="utf-8"))


def save_experiment(experiment: dict[str, Any], raw_stem: str, overwrite: bool) -> tuple[Path, Path]:
    """Save a new experiment YAML and regenerate its prompt output."""
    stem = sanitize_filename_stem(raw_stem)
    input_path = EXPERIMENTS_DIR / f"{stem}_input.yaml"
    output_path = default_output_for_input(input_path, OUTPUTS_DIR)
    if input_path.exists() and not overwrite:
        raise ValueError(f"Refusing to overwrite existing file: {repo_path(input_path)}")
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    input_path.write_text(yaml.safe_dump(experiment, sort_keys=False, allow_unicode=True), encoding="utf-8")
    build_one(load_data_directory(), TEMPLATE_PATH.read_text(encoding="utf-8"), input_path, output_path)
    return input_path, output_path


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    """Show the available local experiment files."""
    if request.method == "POST":
        return handle_submission(None)
    return render_page()


@app.route("/experiment/<path:experiment_name>", methods=["GET", "POST"])
def experiment_preview(experiment_name: str) -> str:
    """Edit, preview, or save one known experiment file."""
    if request.method == "POST":
        return handle_submission(experiment_name)
    paths = experiment_paths()
    input_path = paths.get(experiment_name)
    if input_path is None:
        abort(404)
    experiment = load_yaml(input_path)
    if not isinstance(experiment, dict):
        abort(400, description=f"Experiment must be a YAML mapping: {repo_path(input_path)}")
    try:
        prompt = prompt_for_experiment(experiment)
    except ValueError as exc:
        abort(400, description=str(exc))
    return render_page(selected=experiment_name, experiment_data=experiment, prompt=prompt)


def handle_submission(selected: str | None) -> str:
    """Handle preview and save form actions without mutating original experiments."""
    experiment = experiment_from_form()
    action = request.form.get("action", "preview")
    try:
        prompt = prompt_for_experiment(experiment)
        message = "Preview assembled from edited controls; original experiment YAML was not changed."
        if action == "save":
            input_path, output_path = save_experiment(experiment, request.form.get("filename_stem", ""), request.form.get("overwrite") == "1")
            message = f"Saved {repo_path(input_path)} and regenerated {repo_path(output_path)}."
            selected = input_path.name
        return render_page(selected=selected, experiment_data=experiment, prompt=prompt, message=message)
    except (ValueError, TypeError) as exc:
        return render_page(selected=selected, experiment_data=experiment, error=str(exc)), 400


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
