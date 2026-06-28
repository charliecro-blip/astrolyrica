# Scriptorium UI v0

Scriptorium v0 is a small local web interface for inspecting AstroLyrica experiment inputs and previewing assembled generation prompts. It is intended as a calm writing desk for prompt review, not as a production application or horoscope feed.

## What it does

- Discovers local `experiments/*.yaml` files.
- Shows those experiments in a simple selector.
- Opens a selected experiment at `/experiment/<experiment_name>`.
- Uses the same prompt assembly engine as `src/build_prompt.py`.
- Displays the generated prompt in a copy-friendly textarea.
- Shows basic experiment metadata:
  - planet
  - sign
  - house
  - voice
  - form
  - intent
  - audience
  - occasion
  - variation_seed

## What it does not do yet

- It does not call an LLM or any external generation API.
- It does not save generated poems, horoscopes, image prompts, or other creative outputs.
- It does not post to social platforms.
- It does not include authentication, payments, user accounts, or an external database.
- It does not replace the existing CLI workflows; `src/build_prompt.py` and `src/run_experiments.py` remain the canonical local batch tools.

## Future possible additions

- Edit experiment controls from the browser while keeping YAML human-reviewable.
- Save generated LLM outputs for local review.
- Compare variants across seeds, voices, forms, or symbolic emphases.
- Approve posts for a future publishing workflow.
- Export image prompts for visual generation workflows.
- Add a publishing queue for later Starweather review without performing automatic posting.
