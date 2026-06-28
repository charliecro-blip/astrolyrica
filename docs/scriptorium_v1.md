# Scriptorium UI v1

Scriptorium v1 turns the local prompt preview into a small experiment workbench. It remains a local-only interface: it reads YAML data, assembles prompts, and can save new experiment YAML files, but it does not call an LLM, publish posts, authenticate users, or use an external database.

## Launch the UI

Install dependencies, then launch from the repository root:

~~~bash
pip install -r requirements.txt
python3 src/scriptorium_app.py
~~~

Open:

~~~text
http://127.0.0.1:5000
~~~

## Preview without saving

1. Choose an existing file from the experiment dropdown.
2. Edit the required controls (`planet`, `sign`, `house`, `voice`, `form`) or optional controls.
3. Use one line per item in `emphasize`, `avoid`, `outputs`, and `notes`.
4. Adjust sliders with numeric inputs from `0` to `10`.
5. Click **Preview prompt**.

Preview assembles a prompt from the submitted form data and shows it on the page. It does not overwrite the selected experiment file.

## Save a new experiment

1. Preview or edit an experiment.
2. Enter a safe filename stem, such as `venus_taurus_7th_variant_1`.
3. Click **Save as new experiment**.

The UI writes the YAML to:

~~~text
experiments/<filename_stem>_input.yaml
~~~

It also regenerates the corresponding prompt under:

~~~text
outputs/experiments/<filename_stem>_prompt.md
~~~

If a file already exists, the save is refused unless **Overwrite existing YAML and prompt if present** is checked.

## Filename conventions

- Use lowercase words separated by underscores.
- Include the core symbolic context when useful: `planet_sign_house_variant`.
- Do not include directories or file extensions in the stem.
- Unsafe characters are converted to underscores.
- `_input` is added automatically.

## Limitations

- Local development server only.
- No LLM API calls or generated creative output storage.
- No social posting, authentication, payments, user accounts, or external database.
- Sliders are limited to the common experiment sliders currently exposed in the UI.
- Saved YAML should still be reviewed by a human for symbolic intent and readability.

## Future improvements

- Add richer controls for `controls.include_sections`.
- Compare multiple variants side by side.
- Add lightweight validation messages next to individual fields.
- Support optional custom slider names while keeping YAML reviewable.
