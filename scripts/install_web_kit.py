#!/usr/bin/env python3
"""Copy the compact HSE web kit into a project without overwriting by default."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def copy_tree(source: Path, destination: Path, force: bool) -> int:
    copied = 0
    for item in source.rglob("*"):
        if not item.is_file():
            continue
        target = destination / item.relative_to(source)
        if target.exists() and not force:
            raise FileExistsError(f"Refusing to overwrite {target}; pass --force if intended")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        copied += 1
    return copied


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="Destination folder inside the target project")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    output = args.destination.resolve()
    output.mkdir(parents=True, exist_ok=True)

    try:
        count = copy_tree(skill_root / "assets" / "tokens", output / "css", args.force)
        count += copy_tree(skill_root / "assets" / "fonts", output / "fonts", args.force)
    except FileExistsError as error:
        print(error, file=sys.stderr)
        return 2

    print(f"Copied {count} files to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
