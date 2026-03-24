# pptx-template-editor

A Codex skill and Python toolkit for editing PowerPoint `.pptx` templates without rebuilding the deck from scratch.

It is designed for the workflow most reporting decks actually need:

- inspect an existing template and map slides, placeholders, text boxes, and images
- compare a blank template with a finished deck to derive a reusable fill spec
- fill a template from YAML/JSON without disturbing the original theme or layout
- replace existing image shapes in place
- clone slides by editing Open XML parts directly when repeated sections are needed
- drive the whole workflow from one composition plan

## Why this exists

Most reporting decks already have the right theme, layout, branding, and spacing. Rebuilding them from scratch is brittle. This skill keeps the existing `.pptx` structure and only edits the parts that usually change.

## Install as a Codex skill

If you want Codex to auto-discover and use this as a skill, copy this repository into your Codex skills directory.

### Option 1: clone directly into `~/.codex/skills`

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/cagedbird043/pptx-template-editor.git ~/.codex/skills/pptx-template-editor
```

### Option 2: clone anywhere, then copy or symlink it

```bash
git clone https://github.com/cagedbird043/pptx-template-editor.git
mkdir -p ~/.codex/skills
ln -s "$(pwd)/pptx-template-editor" ~/.codex/skills/pptx-template-editor
```

After that, restart Codex so the new skill is picked up.

## Install Python dependencies

The scripts use a local virtual environment. From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you installed this repo under `~/.codex/skills/pptx-template-editor`, the same commands work there too.

## Features

- `scripts/inspect_pptx.py`
  - inspect slide layouts, shapes, placeholders, text paragraphs, and picture metadata
- `scripts/derive_fill_spec.py`
  - compare a blank template and a completed deck, then emit a reusable YAML/JSON spec
- `scripts/fill_template.py`
  - apply text and image updates to an existing template
- `scripts/clone_slides.py`
  - append cloned copies of existing slides by editing Open XML package parts directly
- `scripts/compose_deck.py`
  - run clone-and-fill in one step from a single YAML/JSON plan

## Use as a Codex skill

Once the repo is under `~/.codex/skills/pptx-template-editor`, Codex can trigger it as a normal skill.

- The skill definition is in `SKILL.md`
- The UI metadata is in `agents/openai.yaml`
- Generic examples live in `references/`

You can also invoke the scripts manually if you prefer explicit commands.

## Use as a standalone tool

```bash
VENV="$(pwd)/.venv/bin/python"
```

## Typical workflow

```bash
"$VENV" scripts/inspect_pptx.py template.pptx --output template-map.yaml
"$VENV" scripts/derive_fill_spec.py template.pptx filled-example.pptx fill-spec.yaml
"$VENV" scripts/fill_template.py template.pptx fill-spec.yaml output.pptx
```

If one content slide needs to be repeated multiple times:

```bash
"$VENV" scripts/clone_slides.py template.pptx expanded.pptx 2 2 3
```

Then inspect the expanded deck and fill the appended slides.

Or do both in one step:

```bash
"$VENV" scripts/compose_deck.py template.pptx references/example_compose_plan.yaml output.pptx
```

## Example fill spec

See `references/example_fill_spec.yaml`.

For the single-file workflow, see `references/example_compose_plan.yaml`.

YAML reminder:

- quote `text` values that contain `:` to avoid YAML parsing errors

## Repository layout

- `SKILL.md`: Codex skill instructions
- `agents/openai.yaml`: UI metadata for the skill
- `scripts/`: executable tools
- `references/`: reusable examples and workflow notes
