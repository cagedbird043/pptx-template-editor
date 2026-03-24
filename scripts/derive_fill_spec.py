#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from _pptx_utils import load_prs, shape_target, shape_text_payload, write_payload


def build_spec(template_path: Path, filled_path: Path) -> dict:
    template = load_prs(template_path)
    filled = load_prs(filled_path)
    if len(template.slides) != len(filled.slides):
        raise ValueError(
            f"Slide count mismatch: template={len(template.slides)} filled={len(filled.slides)}"
        )

    spec = {
        "template": str(template_path),
        "source": str(filled_path),
        "slides": [],
    }

    for slide_number, (tpl_slide, filled_slide) in enumerate(zip(template.slides, filled.slides), start=1):
        updates = []
        max_shapes = max(len(tpl_slide.shapes), len(filled_slide.shapes))
        for shape_index in range(max_shapes):
            if shape_index >= len(tpl_slide.shapes) or shape_index >= len(filled_slide.shapes):
                continue
            tpl_shape = tpl_slide.shapes[shape_index]
            filled_shape = filled_slide.shapes[shape_index]
            tpl_payload = shape_text_payload(tpl_shape)
            filled_payload = shape_text_payload(filled_shape)
            if tpl_payload is None and filled_payload is None:
                continue
            if tpl_payload != filled_payload:
                updates.append(
                    {
                        "target": shape_target(filled_shape, shape_index),
                        "paragraphs": filled_payload["paragraphs"] if filled_payload else [],
                    }
                )
        if updates:
            spec["slides"].append(
                {
                    "slide_number": slide_number,
                    "updates": updates,
                }
            )
    return spec


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Derive a reusable fill spec by comparing a blank template PPTX and a filled PPTX."
    )
    parser.add_argument("template", type=Path)
    parser.add_argument("filled", type=Path)
    parser.add_argument("output", type=Path, help="YAML or JSON spec output path.")
    args = parser.parse_args()

    spec = build_spec(args.template, args.filled)
    write_payload(args.output, spec)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
