#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from pathlib import Path

from _pptx_utils import choose_shape, load_prs, read_payload, replace_shape_image


def apply_paragraphs(text_frame, paragraphs: list[dict]) -> None:
    text_frame.clear()
    if not paragraphs:
        return
    for idx, paragraph_spec in enumerate(paragraphs):
        paragraph = text_frame.paragraphs[0] if idx == 0 else text_frame.add_paragraph()
        paragraph.level = int(paragraph_spec.get("level", 0))
        run = paragraph.add_run()
        run.text = paragraph_spec.get("text", "")
        if "bold" in paragraph_spec:
            run.font.bold = bool(paragraph_spec["bold"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Fill a PPTX template using a YAML or JSON spec.")
    parser.add_argument("template", type=Path)
    parser.add_argument("spec", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    prs = load_prs(args.template)
    spec = read_payload(args.spec)

    for slide_update in spec.get("slides", []):
        slide_number = int(slide_update["slide_number"])
        slide = prs.slides[slide_number - 1]
        for update in slide_update.get("updates", []):
            shape = choose_shape(slide, update["target"])
            if "paragraphs" in update:
                if not hasattr(shape, "text_frame") or shape.text_frame is None:
                    raise TypeError(f"Shape does not have a text frame: {shape.name}")
                apply_paragraphs(shape.text_frame, copy.deepcopy(update.get("paragraphs", [])))
            if "image_path" in update:
                replace_shape_image(slide, shape, Path(update["image_path"]))

    prs.save(str(args.output))
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
