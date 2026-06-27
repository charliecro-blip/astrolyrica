# Generation Prompt

You are generating a short astrological oracle text from structured symbolic inputs.

## Core instruction
Create an original response that synthesizes the selected planet, sign, house, voice, form, and slider settings into one coherent piece.

## Inputs

### Planet
{{planet}}

### Sign
{{sign}}

### House
{{house}}

### Voice
{{voice}}

### Form
{{form}}

### Sliders
{{sliders}}

## Output constraints
- Follow the requested form exactly.
- Preserve the requested voice.
- Use the sliders as intensity controls from 0 to 10.
- Avoid explaining the astrology unless the form asks for explanation.
- Do not mention the slider names directly in the final creative output.
