# Next Codex Build Prompt

Build a local AstroLyrica prototype. Do not implement social posting, LLM API calls, or astrology calculations yet.

## Requirements

1. Load all YAML files from `data/`.
2. Accept manual astrology input from a local JSON or YAML file, such as selected planet, sign, house, aspect, condition, voice, and form IDs.
3. Retrieve matching symbolic entries from the in-repo YAML database.
4. Assemble a prompt package using `prompts/generation_prompt.md`.
5. Check the assembled prompt package for banned phrases.
6. Save outputs to `outputs/experiments/` with a timestamped filename.
7. Add tests or validation commands documenting how to verify parsing and prompt assembly.

## Suggested CLI

```bash
python src/build_prompt.py --input examples/manual_input.yaml --output outputs/experiments/
```

## Constraints

- Keep the system local and deterministic.
- Do not call any LLM API.
- Do not calculate charts or transits.
- Do not post to social platforms.
- Keep generated prompt packages inspectable as Markdown or JSON.
