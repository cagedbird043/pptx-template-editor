#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

from lxml import etree

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

NS = {"p": P_NS, "r": R_NS, "ct": CT_NS}
SLIDE_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
NOTES_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"


def next_rel_id(rels_root) -> str:
    rel_ids = []
    for rel in rels_root.findall(f"{{{REL_NS}}}Relationship"):
        match = re.fullmatch(r"rId(\d+)", rel.get("Id", ""))
        if match:
            rel_ids.append(int(match.group(1)))
    return f"rId{(max(rel_ids) if rel_ids else 0) + 1}"


def clone_slide_rels(data: bytes) -> bytes:
    rels_root = etree.fromstring(data)
    for rel in list(rels_root):
        if rel.get("Type") == NOTES_REL_TYPE:
            rels_root.remove(rel)
    return etree.tostring(rels_root, xml_declaration=True, encoding="UTF-8", standalone="yes")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Append cloned copies of existing slides to a PPTX by editing Open XML parts."
    )
    parser.add_argument("input_pptx", type=Path)
    parser.add_argument("output_pptx", type=Path)
    parser.add_argument(
        "source_slides",
        nargs="+",
        type=int,
        help="1-based slide numbers to clone and append in the given order.",
    )
    args = parser.parse_args()

    with zipfile.ZipFile(args.input_pptx) as zin:
        entries = {name: zin.read(name) for name in zin.namelist() if not name.endswith("/")}

    slide_nums = sorted(
        int(match.group(1))
        for name in entries
        if (match := re.fullmatch(r"ppt/slides/slide(\d+)\.xml", name))
    )
    if not slide_nums:
        raise ValueError("No slides found in the input PPTX")

    presentation_root = etree.fromstring(entries["ppt/presentation.xml"])
    presentation_rels_root = etree.fromstring(entries["ppt/_rels/presentation.xml.rels"])
    content_types_root = etree.fromstring(entries["[Content_Types].xml"])

    sld_id_list = presentation_root.find("p:sldIdLst", NS)
    if sld_id_list is None:
        raise ValueError("presentation.xml does not contain p:sldIdLst")

    next_slide_num = max(slide_nums) + 1
    existing_slide_ids = [int(node.get("id")) for node in sld_id_list.findall("p:sldId", NS)]
    next_slide_id = (max(existing_slide_ids) if existing_slide_ids else 255) + 1

    for source_slide in args.source_slides:
        slide_xml = f"ppt/slides/slide{source_slide}.xml"
        slide_rels = f"ppt/slides/_rels/slide{source_slide}.xml.rels"
        if slide_xml not in entries:
            raise FileNotFoundError(f"Missing source slide: {slide_xml}")

        new_slide_xml = f"ppt/slides/slide{next_slide_num}.xml"
        new_slide_rels = f"ppt/slides/_rels/slide{next_slide_num}.xml.rels"

        entries[new_slide_xml] = entries[slide_xml]
        if slide_rels in entries:
            entries[new_slide_rels] = clone_slide_rels(entries[slide_rels])

        rel_id = next_rel_id(presentation_rels_root)
        etree.SubElement(
            presentation_rels_root,
            f"{{{REL_NS}}}Relationship",
            Id=rel_id,
            Type=SLIDE_REL_TYPE,
            Target=f"slides/slide{next_slide_num}.xml",
        )
        etree.SubElement(
            sld_id_list,
            f"{{{P_NS}}}sldId",
            id=str(next_slide_id),
            **{f"{{{R_NS}}}id": rel_id},
        )
        etree.SubElement(
            content_types_root,
            f"{{{CT_NS}}}Override",
            PartName=f"/ppt/slides/slide{next_slide_num}.xml",
            ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml",
        )

        next_slide_num += 1
        next_slide_id += 1

    entries["ppt/presentation.xml"] = etree.tostring(
        presentation_root, xml_declaration=True, encoding="UTF-8", standalone="yes"
    )
    entries["ppt/_rels/presentation.xml.rels"] = etree.tostring(
        presentation_rels_root, xml_declaration=True, encoding="UTF-8", standalone="yes"
    )
    entries["[Content_Types].xml"] = etree.tostring(
        content_types_root, xml_declaration=True, encoding="UTF-8", standalone="yes"
    )

    with zipfile.ZipFile(args.output_pptx, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name in sorted(entries):
            zout.writestr(name, entries[name])

    print(args.output_pptx)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
