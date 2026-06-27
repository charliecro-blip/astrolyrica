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
### Planet
- Name: Moon
- Keywords: emotion, instinct, memory, need, rhythm
- Prompt text: The Moon speaks through instinct, feeling, memory, attachment, and the body's changing tides.

### Sign
- Name: Scorpio
- Keywords: depth, secrecy, intensity, transformation, devotion
- Prompt text: Scorpio colors the material with emotional depth, private intensity, shadow-work, desire, and transformation.

### House
- Name: Fifth House
- Keywords: creativity, pleasure, romance, play, self-expression
- Prompt text: The fifth house locates the image in creative risk, pleasure, romance, performance, play, and the courage to be seen.

### Symbolic material
- Planetary emphasis: The Moon speaks through instinct, feeling, memory, attachment, and the body's changing tides.
- Zodiacal atmosphere: Scorpio colors the material with emotional depth, private intensity, shadow-work, desire, and transformation.
- House arena: The fifth house locates the image in creative risk, pleasure, romance, performance, play, and the courage to be seen.

### Voice
- Name: Modern Oracle
- Keywords: intimate, lucid, symbolic, contemporary, numinous
- Prompt text: Write in a modern oracle voice: clear, intimate, symbol-rich, contemporary, and spiritually charged without sounding archaic.

### Form
- Name: Five-Line Oracle
- Keywords: concise, poetic, five lines, complete image
- Prompt text: Return exactly five lines. Each line should feel complete, imagistic, and necessary. Do not add a title or explanation.

### Sliders
- imagery: 8/10
- surrealism: 6/10
- embodiment: 7/10
- technical_astrology: 2/10
- darkness: 5/10
- instruction: 4/10

## Generation task
Create an original response that blends the astrology context, symbolic material, voice, form, and slider settings into one coherent piece.

## Output constraints
- Follow the requested form exactly.
- Preserve the requested voice.
- Use sliders as 0–10 intensity controls.
- Avoid explaining the astrology unless the form asks for explanation.
- Return only the creative output, with no prefatory note or analysis.
