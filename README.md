# AstroLyrica

AstroLyrica is a prompt-building workspace for structured astrological writing experiments. It keeps symbolic source material, prompt templates, experiment inputs, and generated prompt drafts in separate modules so prompts can be assembled reproducibly before a human pastes them into an LLM.

## Project overview

The project is intentionally small and file-based:

- `data/` stores reusable YAML source entries for planets, signs, houses, voices, and forms.
- `experiments/` stores individual experiment input files that select which source entries and slider values to use.
- `prompts/` stores reusable prompt templates.
- `src/` stores local utility scripts.
- `outputs/` stores generated prompt files for manual review and copy/paste.

No script in this repository should call an LLM directly unless a future workflow explicitly adds that behavior.

## Setup

Use Python 3 from the repository root. The current prompt builder uses only the Python standard library, so no package installation is required.

```bash
python3 --version
```

## First manual experiment workflow

The first experiment input lives at:

```text
experiments/moon_scorpio_5th_input.yaml
```

It selects Moon in Scorpio in the fifth house, using the `modern_oracle` voice and the `five_line_oracle` form. Slider values are stored in the same file and are interpreted as 0–10 intensity controls.

### Build the prompt

Run this from the repository root:

```bash
python3 src/build_prompt.py
```

The script loads:

- the experiment input from `experiments/moon_scorpio_5th_input.yaml`
- matching YAML entries from `data/planets`, `data/signs`, `data/houses`, `data/voices`, and `data/forms`
- the reusable generation template from `prompts/generation_prompt.md`

It writes the assembled prompt to:

```text
outputs/experiments/moon_scorpio_5th_prompt.md
```

No LLM is called. Copy the generated Markdown prompt into Claude, ChatGPT, or another model manually.

### Optional custom paths

You can pass a custom input and output path:

```bash
python3 src/build_prompt.py experiments/moon_scorpio_5th_input.yaml outputs/experiments/moon_scorpio_5th_prompt.md
```

The custom input must use the same keys: `planet`, `sign`, `house`, `voice`, `form`, and `sliders`.
