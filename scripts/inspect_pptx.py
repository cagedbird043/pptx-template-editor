#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from _pptx_utils import (
    load_prs,
    shape_image_payload,
    shape_target,
    shape_text_payload,
    write_payload,
)


def build_report(path: Path) -> dict:
    prs = load_prs(path)
    report = {
        "path": str(path),
        "slide_count": len(prs.slides),
        "slide_layout_count": len(prs.slide_layouts),
        "slides": [],
    }
    for slide_number, slide in enumerate(prs.slides, start=1):
        slide_info = {
            "slide_number": slide_number,
            "layout_name": slide.slide_layout.name,
            "shapes": [],
        }
        for shape_index, shape in enumerate(slide.shapes):
            item = {
                **shape_target(shape, shape_index),
                "shape_type": str(shape.shape_type),
                "has_text": bool(hasattr(shape, "text_frame") and shape.text_frame is not None),
            }
            text_payload = shape_text_payload(shape)
            if text_payload is not None:
                item.update(text_payload)
            image_payload = shape_image_payload(shape)
            if image_payload is not None:
                item.update(image_payload)
            slide_info["shapes"].append(item)
        report["slides"].append(slide_info)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect slide, shape, and text structure inside a .pptx file.")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--output", type=Path, help="Write YAML or JSON report to this path.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    args = parser.parse_args()

    report = build_report(args.pptx)
    if args.output:
        write_payload(args.output, report)
        print(args.output)
        return 0

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    print(f"PPTX: {args.pptx}")
    print(f"Slides: {report['slide_count']}  Layouts: {report['slide_layout_count']}")
    for slide in report["slides"]:
        print(f"- Slide {slide['slide_number']}: layout={slide['layout_name']!r}, shapes={len(slide['shapes'])}")
        for shape in slide["shapes"]:
            desc = f"  - [{shape['shape_index']}] {shape['shape_name']!r} type={shape['shape_type']}"
            if "placeholder_idx" in shape:
                desc += f" placeholder_idx={shape['placeholder_idx']}"
            print(desc)
            if shape.get("has_text"):
                for paragraph_index, paragraph in enumerate(shape["paragraphs"]):
                    extra = []
                    if paragraph.get("bold") is True:
                        extra.append("bold")
                    if paragraph.get("level") is not None:
                        extra.append(f"level={paragraph['level']}")
                    suffix = f" [{' '.join(extra)}]" if extra else ""
                    print(f"    - p{paragraph_index}: {paragraph['text']}{suffix}")
            if "image_filename" in shape:
                print(
                    "    - image: "
                    f"{shape['image_filename']} ext={shape['image_ext']} "
                    f"size={tuple(shape['image_size'])} sha1={shape['image_sha1']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
