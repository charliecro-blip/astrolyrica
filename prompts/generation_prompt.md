# AstroLyrica Generation Template

Use this reusable template to generate a concise astrological oracle from structured source material. The builder script replaces the uppercase placeholders below before the prompt is pasted into an LLM.

## Source rules
- Treat the provided context as the only source material.
- Synthesize the inputs rather than listing them separately in the final creative response.
- Do not invent extra chart placements, aspects, transits, or biographical details.
- Keep technical astrology subtle unless the slider settings ask for more explicit technique.
- Do not mention placeholder names, data keys, or slider names in the final creative output.

## Module descriptions

### Astrology context
ASTROLOGY_CONTEXT

### Symbolic material
SYMBOLIC_MATERIAL

### Voice
VOICE

### Form
FORM

### Sliders
SLIDERS

## Generation task
Create an original response that blends the astrology context, symbolic material, voice, form, and slider settings into one coherent piece.

## Output constraints
- Follow the requested form exactly.
- Preserve the requested voice.
- Use sliders as 0–10 intensity controls.
- Avoid explaining the astrology unless the form asks for explanation.
- Return only the creative output, with no prefatory note or analysis.
