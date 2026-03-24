# Template Patterns

Use this skill when the template already looks correct and the work is mostly about content.

## Good fits

- performance reviews
- quarterly business reviews
- project updates
- training decks with repeated section slides
- cover pages with a fixed hero image and a replaceable profile image

## Common patterns

### Fixed deck, text only

Use `inspect_pptx.py` and `fill_template.py`.

### Learn from one successful deck

Use `derive_fill_spec.py` to reverse engineer a reusable YAML/JSON spec from a blank template and a finished deck.

### Repeated sections

Use `clone_slides.py` first, then fill the appended slides.

### Image swap without moving layout

Target an existing picture shape and set `image_path` in the update spec.
