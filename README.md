# pptx-template-editor

A Codex-friendly PowerPoint template editing skill for `.pptx` decks.

It focuses on the pragmatic workflow that works well for internal reporting decks:

- inspect an existing template and map slides, placeholders, text boxes, and images
- compare a blank template with a finished deck to derive a reusable fill spec
- fill a template from YAML/JSON without disturbing the original theme or layout
- replace existing image shapes in place
- clone slides by editing Open XML parts directly when repeated sections are needed
- drive the whole workflow from one composition plan

## Why this exists

Most reporting decks already have the right theme, layout, branding, and spacing. Rebuilding them from scratch is brittle. This skill keeps the existing `.pptx` structure and only edits the parts that usually change.

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

## Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Typical workflow

```bash
VENV="$(pwd)/.venv/bin/python"

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

## Codex skill layout

This repo is also structured as a Codex skill folder, so it can be dropped into `~/.codex/skills/pptx-template-editor` directly.
