---
name: pptx-template-editor
description: Inspect, compare, and fill PowerPoint `.pptx` templates while preserving the existing master, layouts, and object positions. Use when Codex needs to (1) map slides and placeholders in a template, (2) reverse engineer a finished deck against a blank template, or (3) generate a new `.pptx` by replacing text or images in known shapes without rebuilding the presentation from scratch.
---

# PPTX Template Editor

Use this skill when the user already has a `.pptx` template and wants an editable output deck that keeps the original theme, layouts, images, and slide geometry.

## Quick Start

Always use the skill-local venv:

```bash
VENV="$(pwd)/.venv/bin/python"
```

Run the workflow in this order:

1. Inspect the template structure.
2. If a finished example exists, derive a reusable fill spec from it.
3. Fill the template with that spec or with a hand-written YAML/JSON spec.
4. If the deck needs repeated sections, either clone slides first or use a single compose plan.
5. Re-inspect or diff the generated deck before declaring success.

## Workflow

### 1. Inspect a template before editing

Use `scripts/inspect_pptx.py` to map slide numbers, layout names, shape names, placeholder indices, paragraph text, and picture metadata.

```bash
"$VENV" scripts/inspect_pptx.py template.pptx
"$VENV" scripts/inspect_pptx.py template.pptx --output template-map.yaml
```

Prefer targets in this order:

- `placeholder_idx` when the shape is a real placeholder
- `shape_name` when the template uses stable names
- `shape_index` as a last-resort fallback inside one known template

Do not assume shape order is portable across unrelated templates.

### 2. Learn a template from a finished deck

If the user gives you both a blank template and a completed deck, derive a spec with `scripts/derive_fill_spec.py`.

```bash
"$VENV" scripts/derive_fill_spec.py blank-template.pptx filled-example.pptx fill-spec.yaml
```

This is the fastest way to learn:

- which slides actually changed
- which shapes carry text
- how many paragraphs each target shape expects
- which paragraphs were bolded

Use this whenever you want to clone the user's prior formatting choices instead of guessing.

### 3. Generate a new deck from a spec

Use `scripts/fill_template.py`.

```bash
"$VENV" scripts/fill_template.py blank-template.pptx fill-spec.yaml output.pptx
```

The fill spec contains slide-local updates. Each update points to one editable shape and replaces its content.

Example:

```yaml
slides:
  - slide_number: 2
    updates:
      - target:
          shape_name: Content Placeholder 2
          placeholder_idx: 1
        paragraphs:
          - text: "Objective 1: Launch feature A"
            bold: true
          - text: Delivered API, docs, and validation.
          - text: "Objective 2: Improve platform stability"
            bold: true
          - text: Reduced incident volume and improved diagnostics.
```

Rules:

- one YAML paragraph becomes one PowerPoint paragraph
- `bold: true` sets the inserted run bold
- `level` can be used for nested bullets when needed
- `image_path` can replace an existing picture shape without moving it
- the script edits existing shapes only; it does not redraw charts
- quote `text` values that contain `:` so the YAML stays valid

### 4. Clone repeated slides when XML-level duplication is needed

Use `scripts/clone_slides.py` to append copies of existing slides at the end of the deck. This script edits the Open XML package directly and is useful when one template slide needs to be reused multiple times.

```bash
"$VENV" scripts/clone_slides.py template.pptx expanded.pptx 2 2 3
```

The example above keeps the original deck intact and appends clones of slide 2, slide 2, and slide 3.

Current guardrails:

- designed for appending clones, not arbitrary reordering
- works best for ordinary content slides
- cloned slide note relationships are dropped on purpose to avoid collisions

After cloning, inspect the new slide numbers and then run `fill_template.py` against the expanded deck.

### 5. Use a single compose plan for clone-and-fill workflows

Use `scripts/compose_deck.py` when one YAML/JSON file should drive the entire workflow.

```bash
"$VENV" scripts/compose_deck.py template.pptx references/example_compose_plan.yaml output.pptx
```

`clone_append` lists source slides to append before any updates are applied:

```yaml
clone_append: [2, 2, 3]
slides:
  - slide_number: 6
    updates:
      - target:
          shape_name: Title 1
        paragraphs:
          - text: "Objective 3"
```

This is the best default for automated generation because it keeps one source of truth instead of juggling an expanded intermediate deck plus a separate fill spec.

### 6. Validate the result

Use one of these checks:

- re-run `inspect_pptx.py` on the output and confirm target paragraphs or image metadata
- derive a spec between the expected finished deck and your generated deck; an empty `slides: []` means the text payload matches
- if the user cares about pixel-level QA, open the deck manually or add a rendering step outside this skill

## Decision Rules

Prefer this skill when:

- the template already looks right and only content changes
- the user wants to preserve corporate styling from an existing `.pptx`
- you need a reproducible YAML/JSON representation of deck content
- you want to learn a template from one successful example and reuse it later

Do not overuse this skill for tasks it does not yet automate well:

- arbitrary slide reordering across many layouts
- SmartArt editing
- embedded chart workbook editing
- complex animation timelines
- arbitrary geometry/layout redesign

For those cases, inspect first, then decide whether a raw Open XML fallback is truly needed.

## Resources

### scripts/

- `scripts/inspect_pptx.py`: inspect slide layouts, shapes, placeholders, text, and image metadata
- `scripts/derive_fill_spec.py`: compare a blank template and a finished deck to derive reusable YAML/JSON updates
- `scripts/fill_template.py`: apply text and image updates to a template and write a new `.pptx`
- `scripts/clone_slides.py`: append cloned copies of existing slides by editing Open XML parts directly
- `scripts/compose_deck.py`: clone slides and apply updates from one plan file
- `scripts/_pptx_utils.py`: shared helpers for payload IO, image replacement, and shape targeting

### references/

- `references/template_patterns.md`: generic guidance for common template workflows
- `references/example_fill_spec.yaml`: sanitized example spec showing text and image replacement
