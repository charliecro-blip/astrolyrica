# AstroLyrica

AstroLyrica is an astrological poetry engine that turns structured symbolic astrology data into poems, daily horoscopes, image prompts, and eventually social posts. The project begins as a local data-and-prompt system: curated YAML entries feed reusable generation prompts while outputs are saved for review and refinement.

## Internal modules

- **Celestial Dictionarium** — the symbolic language database of planets, signs, houses, aspects, conditions, voices, forms, source notes, and banned phrases.
- **Decan Engine** — the generation system that retrieves symbolic entries, assembles meaning briefs, and formats generation prompts for poems, horoscopes, and images.
- **Starweather** — the future daily publishing bot for recurring horoscopes and social-ready material.
- **Scriptorium** — the future review and editing dashboard for inspecting generated work, tuning voice, and approving outputs.


## Project operating docs

Future Codex tasks should use these repository operating documents instead of relying on repeated pasted prompts:

- [AGENTS.md](AGENTS.md) — project-wide instructions and scope boundaries for Codex work.
- [Build tracks](docs/build_tracks.md) — major work tracks for symbolic data, prompt assembly, experiments, Scriptorium, and Starweather preparation.
- [Implementation sequence](docs/implementation_sequence.md) — recommended order for building AstroLyrica from local foundations toward later automation.

## Current scope

This initial repository does not implement social posting, LLM API calls, or astrology calculations. It provides the starter data structure, documentation, prompt templates, and a YAML validation script.

## Local Scriptorium UI

The Scriptorium UI is a minimal local Flask interface for browsing `experiments/*.yaml` files and previewing the same assembled prompts produced by the CLI workflow. It does not call an LLM, save generated creative outputs, or add publishing/account features.

Install dependencies and launch it from the repository root:

~~~bash
pip install -r requirements.txt
python3 src/scriptorium_app.py
~~~

Then open:

~~~text
http://127.0.0.1:5000
~~~

Use the experiment dropdown to choose a local YAML file and copy the generated prompt from the preview area.

## Validate the data

Install dependencies and run the validator:

```bash
pip install -r requirements.txt
python src/validate_data.py
```

## First manual experiment workflow

The first experiment input lives at:

~~~text
experiments/moon_scorpio_5th_input.yaml
~~~

It selects Moon in Scorpio in the fifth house, using the `modern_oracle` voice and the `five_line_oracle` form. Slider values are stored in the same file and are interpreted as 0–10 intensity controls.

### Build the prompt

Run this from the repository root:

~~~bash
python3 src/build_prompt.py
~~~

The script loads:

- the experiment input from `experiments/moon_scorpio_5th_input.yaml`
- matching YAML entries from `data/planets.yaml`, `data/signs.yaml`, `data/houses.yaml`, `data/voices.yaml`, and `data/forms.yaml`
- the reusable generation template from `prompts/generation_prompt.md`

It writes the assembled prompt to:

~~~text
outputs/experiments/moon_scorpio_5th_prompt.md
~~~

No LLM is called. Copy the generated Markdown prompt into Claude, ChatGPT, or another model manually.

### Optional custom paths

You can pass a custom input and output path:

~~~bash
python3 src/build_prompt.py experiments/moon_scorpio_5th_input.yaml outputs/experiments/moon_scorpio_5th_prompt.md
~~~

The custom input must use the same keys: `planet`, `sign`, `house`, `voice`, `form`, and `sliders`. It may also include `controls.include_sections` booleans for `combination_notes`, `commonplace_images`, and `sliders`, plus `controls.outputs` to choose the requested sections in the generated prompt.

### Batch prompt generation

Run one experiment from the repository root:

~~~bash
python3 src/build_prompt.py
~~~

This preserves the manual Moon/Scorpio/5th experiment and writes:

~~~text
outputs/experiments/moon_scorpio_5th_prompt.md
~~~

Run all local experiment inputs from the repository root:

~~~bash
python3 src/run_experiments.py
~~~

The batch runner discovers every YAML file in `experiments/`, writes generated prompts to `outputs/experiments/`, and updates `outputs/experiments/batch_summary.md` so local experiments can be reviewed without opening every prompt file.

`src/build_prompt.py --batch` remains available for compatibility, but `src/run_experiments.py` is the dedicated experiment runner.
