#!/usr/bin/env python3
"""Local Scriptorium UI for previewing AstroLyrica experiment prompts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from flask import Flask, abort, render_template_string, url_for

from prompt_engine import (
    DATA_KEYS,
    EXPERIMENTS_DIR,
    TEMPLATE_PATH,
    assemble_prompt,
    discover_experiments,
    find_combination_notes,
    find_entry,
    load_data_directory,
    load_optional_commonplace_images,
    load_yaml,
    repo_path,
    resolve_id,
)

app = Flask(__name__)

PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AstroLyrica Scriptorium</title>
  <style>
    :root { color-scheme: light; }
    body {
      margin: 0;
      background: #f4efe6;
      color: #2f251c;
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.5;
    }
    main { max-width: 1120px; margin: 0 auto; padding: 3rem 1.5rem 4rem; }
    header { border-bottom: 1px solid #d7cbbb; margin-bottom: 1.5rem; padding-bottom: 1rem; }
    h1 { font-size: clamp(2rem, 4vw, 3.5rem); margin: 0; font-weight: 500; letter-spacing: .02em; }
    .subtitle { margin: .4rem 0 0; color: #6c5b4a; }
    .desk {
      display: grid;
      grid-template-columns: minmax(240px, 320px) 1fr;
      gap: 1.25rem;
      align-items: start;
    }
    .panel {
      background: #fffaf1;
      border: 1px solid #d8c9b4;
      border-radius: 14px;
      box-shadow: 0 12px 40px rgba(77, 56, 35, .08);
      padding: 1rem;
    }
    label, .label { display: block; color: #6a4d34; font-size: .86rem; letter-spacing: .08em; text-transform: uppercase; }
    select {
      box-sizing: border-box;
      width: 100%;
      margin-top: .4rem;
      padding: .7rem;
      border: 1px solid #c7b59d;
      border-radius: 10px;
      background: #fffdf8;
      color: #2f251c;
      font: inherit;
    }
    .meta { display: grid; gap: .6rem; margin-top: 1rem; }
    .meta div { border-top: 1px solid #eadfce; padding-top: .55rem; }
    .meta strong { display: block; font-size: .78rem; color: #7c6045; text-transform: uppercase; letter-spacing: .07em; }
    .meta span { overflow-wrap: anywhere; }
    textarea {
      box-sizing: border-box;
      width: 100%;
      min-height: 70vh;
      padding: 1rem;
      border: 1px solid #c7b59d;
      border-radius: 12px;
      background: #fffdf8;
      color: #241c15;
      font: 0.95rem/1.45 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      resize: vertical;
      white-space: pre;
    }
    .empty { padding: 2rem; color: #6c5b4a; }
    a { color: #704214; text-decoration-thickness: 1px; }
    @media (max-width: 760px) { .desk { grid-template-columns: 1fr; } main { padding-top: 1.5rem; } }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Scriptorium</h1>
      <p class="subtitle">A local writing desk for browsing experiment YAML and previewing assembled AstroLyrica prompts.</p>
    </header>
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
        {% if metadata %}
          <div class="meta">
            {% for key, value in metadata.items() %}
              <div><strong>{{ key.replace('_', ' ') }}</strong><span>{{ value }}</span></div>
            {% endfor %}
          </div>
        {% endif %}
      </aside>
      <section class="panel">
        {% if prompt %}
          <div class="label">Generated prompt preview</div>
          <textarea readonly spellcheck="false">{{ prompt }}</textarea>
        {% else %}
          <div class="empty">Select an experiment to preview the assembled prompt. This interface only reads local YAML and does not call an LLM or save creative outputs.</div>
        {% endif %}
      </section>
    </section>
  </main>
</body>
</html>
"""

METADATA_FIELDS = (
    "planet",
    "sign",
    "house",
    "voice",
    "form",
    "intent",
    "audience",
    "occasion",
    "variation_seed",
)


def experiment_paths() -> dict[str, Path]:
    """Return route-safe experiment file names mapped to paths."""
    return {path.name: path for path in discover_experiments(EXPERIMENTS_DIR)}


def render_page(
    selected: str | None = None,
    prompt: str = "",
    metadata: dict[str, Any] | None = None,
) -> str:
    """Render the shared Scriptorium page."""
    experiments = [{"name": name} for name in experiment_paths()]
    return render_template_string(
        PAGE_TEMPLATE,
        experiments=experiments,
        selected=selected,
        prompt=prompt,
        metadata=metadata or {},
    )


@app.get("/")
def index() -> str:
    """Show the available local experiment files."""
    return render_page()


@app.get("/experiment/<path:experiment_name>")
def experiment_preview(experiment_name: str) -> str:
    """Preview the assembled prompt for one known experiment file."""
    paths = experiment_paths()
    input_path = paths.get(experiment_name)
    if input_path is None:
        abort(404)

    experiment = load_yaml(input_path)
    if not isinstance(experiment, dict):
        abort(400, description=f"Experiment must be a YAML mapping: {repo_path(input_path)}")

    try:
        data = load_data_directory()
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
        entries = {
            kind: find_entry(data, kind, resolve_id(kind, experiment.get(kind)))
            for kind in DATA_KEYS
        }
        prompt = assemble_prompt(
            experiment,
            entries,
            template,
            load_optional_commonplace_images(data),
            find_combination_notes(data, entries),
        )
    except ValueError as exc:
        abort(400, description=str(exc))

    metadata = {field: experiment.get(field, "") for field in METADATA_FIELDS}
    return render_page(selected=experiment_name, prompt=prompt, metadata=metadata)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
