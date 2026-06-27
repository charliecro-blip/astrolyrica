# AstroLyrica

AstroLyrica is an astrological poetry engine that turns structured symbolic astrology data into poems, daily horoscopes, image prompts, and eventually social posts. The project begins as a local data-and-prompt system: curated YAML entries feed reusable generation prompts while outputs are saved for review and refinement.

## Internal modules

- **Celestial Dictionarium** — the symbolic language database of planets, signs, houses, aspects, conditions, voices, forms, source notes, and banned phrases.
- **Decan Engine** — the generation system that retrieves symbolic entries, assembles meaning briefs, and formats generation prompts for poems, horoscopes, and images.
- **Starweather** — the future daily publishing bot for recurring horoscopes and social-ready material.
- **Scriptorium** — the future review and editing dashboard for inspecting generated work, tuning voice, and approving outputs.

## Current scope

This initial repository does not implement social posting, LLM API calls, or astrology calculations. It provides the starter data structure, documentation, prompt templates, a YAML validation script, and a first manual experiment workflow.

## Validate the data

Check that Python is available:

~~~bash
python3 --version
~~~

Install dependencies if needed:

~~~bash
pip install -r requirements.txt
~~~

Validate the YAML files:

~~~bash
python3 src/validate_data.py
~~~

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

The custom input must use the same keys: `planet`, `sign`, `house`, `voice`, `form`, and `sliders`.

## Near-term goal

The first success condition is simple: generate one strong, astrologically coherent test prompt for “Moon in Scorpio in the fifth house,” paste it into an LLM, and see whether the output feels close to publishable.
