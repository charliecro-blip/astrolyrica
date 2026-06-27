# AstroLyrica Generation Prompt Template

Use the supplied symbolic entries to generate original AstroLyrica output. Do not copy source prose. Do not use banned phrases.

## Inputs

- Astrology input: `{manual_astrology_input}`
- Retrieved planets: `{planet_entries}`
- Retrieved signs: `{sign_entries}`
- Retrieved houses: `{house_entries}`
- Retrieved aspects: `{aspect_entries}`
- Retrieved conditions: `{condition_entries}`
- Voice preset: `{voice_entry}`
- Form constraints: `{form_entry}`
- Banned phrases: `{banned_phrases}`
- Desired poem length: `{x_length}`

## Task

Create the following five outputs:

### 1. Meaning brief

Write a concise interpretive brief explaining the symbolic logic. Include:

- Core astrological configuration.
- Main emotional weather.
- Constructive use.
- Shadow or caution.
- One practical action.

### 2. X-length poem

Write an original poem of approximately `{x_length}`. Use concrete images, active verbs, and the selected voice preset. Avoid generic astrology language and all banned phrases.

### 3. Five-line oracle

Write exactly five lines:

1. Core symbol or tension.
2. Vivid image.
3. Turn, warning, or threshold.
4. Medicine or practical gesture.
5. Memorable closing imperative or blessing.

### 4. Daily horoscope paragraph

Write one grounded daily horoscope paragraph. Include one emotional theme, one practical action, and one gentle caution. Keep it useful, humane, and specific.

### 5. Image prompt

Write an image-generation prompt describing subject, setting, composition, palette, atmosphere, and symbolic objects. Do not request visible text in the image.

## Quality checks

Before finalizing, confirm:

- No banned phrases are present.
- No source phrasing has been copied.
- The output matches the requested voice and form.
- The symbolism is specific enough to trace back to the retrieved entries.
