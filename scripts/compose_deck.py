#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from _pptx_utils import read_payload
from clone_slides import clone_slides_file
from fill_template import fill_template_file


def compose_deck(template_path: Path, plan: dict, output_path: Path) -> None:
    clone_sequence = [int(item) for item in plan.get("clone_append", [])]
    working_input = template_path

    with tempfile.TemporaryDirectory(prefix="pptx-compose-") as tmpdir:
        if clone_sequence:
            expanded = Path(tmpdir) / "expanded.pptx"
            clone_slides_file(template_path, expanded, clone_sequence)
            working_input = expanded

        fill_template_file(working_input, plan, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose a deck from a single YAML/JSON plan that can clone slides and fill content."
    )
    parser.add_argument("template", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    plan = read_payload(args.plan)
    compose_deck(args.template, plan, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
