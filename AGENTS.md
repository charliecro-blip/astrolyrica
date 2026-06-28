# AstroLyrica operating instructions

AstroLyrica is an astrological poetry engine. Treat it as a symbolic, literary, and interpretive system rather than a generic horoscope generator.

## Project intent

- Preserve AstroLyrica's symbolic intelligence, relational interpretation, originality guardrails, and poetic specificity.
- Do not reduce the project to generic horoscope generation or flattened zodiac copy.
- Prefer small, coherent modules over large abstractions.
- Keep YAML data human-editable and easy to review.
- Preserve copyright hygiene: do not copy distinctive phrasing from modern authors, copyrighted poems, or source texts.

## Scope boundaries

- Do not add LLM API calls unless explicitly requested.
- Do not add social posting unless explicitly requested.
- Do not add payment, authentication, or user account systems unless explicitly requested.

## Data, prompts, and generated files

- Run `python3 src/validate_data.py` after changing YAML data.
- Run `python3 src/build_prompt.py` after changing prompt generation behavior.
- Keep generated prompt files updated when generator behavior changes.

## Communication

- Summarize files changed and commands run in final responses.
