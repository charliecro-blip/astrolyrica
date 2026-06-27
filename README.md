# AstroLyrica

AstroLyrica is an astrological poetry engine that turns structured symbolic astrology data into poems, daily horoscopes, image prompts, and eventually social posts. The project begins as a local data-and-prompt system: curated YAML entries feed reusable generation prompts while outputs are saved for review and refinement.

## Internal modules

- **Celestial Dictionarium** — the symbolic language database of planets, signs, houses, aspects, conditions, voices, forms, source notes, and banned phrases.
- **Decan Engine** — the generation system that retrieves symbolic entries, assembles meaning briefs, and formats generation prompts for poems, horoscopes, and images.
- **Starweather** — the future daily publishing bot for recurring horoscopes and social-ready material.
- **Scriptorium** — the future review and editing dashboard for inspecting generated work, tuning voice, and approving outputs.

## Current scope

This initial repository does not implement social posting, LLM API calls, or astrology calculations. It provides the starter data structure, documentation, prompt templates, and a YAML validation script.

## Validate the data

Install dependencies and run the validator:

```bash
pip install -r requirements.txt
python src/validate_data.py
```
