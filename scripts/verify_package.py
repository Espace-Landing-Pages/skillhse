#!/usr/bin/env python3
"""Verify required downloads, archives, tokens, fonts, and unpacked HSE assets."""

from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path

from unpack_brand_assets import ARCHIVES, FILES


EXPECTED_COLORS = {
    "#0F2D69",
    "#234B9B",
    "#929292",
    "#C6C6C6",
    "#E6E6E6",
    "#0FA0D7",
    "#009B64",
    "#EB691E",
    "#7D50B9",
    "#E61E3C",
    "#FAB900",
    "#7DA0D2",
    "#CDDCF0",
    "#46A0A0",
    "#D7EBB4",
    "#EB8C3C",
    "#FFDC91",
    "#96648C",
    "#D7C3F0",
    "#CD5A5A",
    "#F5C3C3",
    "#FFD746",
    "#FFF07D",
}

EXPECTED_FONTS = {
    "hse-sans/HSESans-Thin.otf",
    "hse-sans/HSESans-Regular.otf",
    "hse-sans/HSESans-Italic.otf",
    "hse-sans/HSESans-SemiBold.otf",
    "hse-sans/HSESans-Bold.otf",
    "hse-sans/HSESans-Black.otf",
    "hse-slab/HSESlab-Regular.otf",
    "hse-slab/HSESlab-Italic.otf",
    "hse-slab/HSESlab-Black.otf",
}


def collect_hex(value: object) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for child in value.values():
            found |= collect_hex(child)
    elif isinstance(value, list):
        for child in value:
            found |= collect_hex(child)
    elif isinstance(value, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        found.add(value.upper())
    return found


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    downloads = root / "assets" / "original-downloads"
    official = root / "assets" / "official"
    errors: list[str] = []

    for filename in (*ARCHIVES, *FILES):
        if not (downloads / filename).is_file():
            errors.append(f"missing source: {filename}")

    for filename in ARCHIVES:
        path = downloads / filename
        if not path.is_file():
            continue
        if not zipfile.is_zipfile(path):
            errors.append(f"not a ZIP archive: {filename}")
            continue
        with zipfile.ZipFile(path) as package:
            broken = package.testzip()
            if broken:
                errors.append(f"broken ZIP member in {filename}: {broken}")

    token_path = root / "assets" / "tokens" / "hse.tokens.json"
    try:
        tokens = json.loads(token_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"invalid tokens JSON: {error}")
        tokens = {}
    actual_colors = collect_hex(tokens.get("color", {})) if isinstance(tokens, dict) else set()
    if actual_colors != EXPECTED_COLORS:
        errors.append(
            "token colors differ: "
            f"missing={sorted(EXPECTED_COLORS - actual_colors)}, "
            f"extra={sorted(actual_colors - EXPECTED_COLORS)}"
        )

    font_root = root / "assets" / "fonts"
    actual_fonts = {
        str(path.relative_to(font_root))
        for path in font_root.rglob("*.otf")
        if path.is_file()
    }
    if actual_fonts != EXPECTED_FONTS:
        errors.append(
            "font inventory differs: "
            f"missing={sorted(EXPECTED_FONTS - actual_fonts)}, "
            f"extra={sorted(actual_fonts - EXPECTED_FONTS)}"
        )

    for path in font_root.rglob("*.otf"):
        if path.read_bytes()[:4] != b"OTTO":
            errors.append(f"invalid OTF header: {path.relative_to(root)}")

    metadata = [
        path
        for path in official.rglob("*")
        if path.name == ".DS_Store"
        or path.name.startswith("._")
        or "__MACOSX" in path.parts
    ]
    if metadata:
        errors.append(f"macOS metadata found: {len(metadata)} entries")

    unpacked_files = sum(1 for path in official.rglob("*") if path.is_file())
    if unpacked_files < 900:
        errors.append(f"unexpectedly small unpacked inventory: {unpacked_files} files")

    guide = official / "guidelines" / "HSE-brandbook-2026-04-10.pdf"
    if not guide.is_file() or guide.read_bytes()[:4] != b"%PDF":
        errors.append("missing or invalid 2026 brandbook PDF")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(ARCHIVES)} archives, {len(actual_fonts)} fonts, "
        f"{len(actual_colors)} colors, {unpacked_files} unpacked files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
