# Astrolyrica

Astrolyrica is a prompt-building workspace for manual astrology writing experiments.

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
- the prompt template from `prompts/generation_prompt.md`

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
