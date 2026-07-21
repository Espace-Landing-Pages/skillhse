#!/usr/bin/env python3
"""Safely unpack the official HSE brandbook downloads into named folders."""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import zipfile
import zlib
from pathlib import Path, PurePosixPath


ARCHIVES = {
    "533607715": "logos/core/full-russian/light",
    "533607861": "logos/core/full-russian/dark",
    "1145262286.zip": "logos/core/short-russian/light",
    "1145262347.zip": "logos/core/short-russian/dark",
    "533608658": "logos/core/short-full-descriptor/light",
    "533608704": "logos/core/short-full-descriptor/dark",
    "533608945": "logos/core/one-line/light",
    "533608992": "logos/core/one-line/dark",
    "533609036": "logos/core/sign/light",
    "533609051": "logos/core/sign/dark",
    "533609239": "logos/divisions/two-line-descriptor",
    "533609249": "logos/divisions/three-line-descriptor",
    "533610866": "logos/divisions/with-departments/variant-1",
    "533610897": "logos/divisions/with-departments/variant-2",
    "533610952": "logos/divisions/with-departments/variant-3",
    "533611114": "logos/divisions/short",
    "591248341.zip": "logos/international/full/light",
    "591248428.zip": "logos/international/full/dark",
    "533611179": "logos/international/short/light",
    "533611217": "logos/international/short/dark",
    "1145353171.zip": "logos/campuses/saint-petersburg",
    "1145409818.zip": "logos/campuses/nizhny-novgorod",
    "1145405648.zip": "logos/campuses/perm",
    "912504036.zip": "logos/campuses/online",
    "1145614883.zip": "graphic-elements/abbreviation/russian",
    "1145614990.zip": "graphic-elements/abbreviation/english",
    "533611612": "graphic-elements/motto",
    "533611656": "graphic-elements/mascot",
    "533611868": "fonts/hse-sans",
    "533611928": "fonts/hse-slab",
    "665895213.zip": "templates/latex",
}

FILES = {
    "1159194524.pptx": "templates/presentation/hse-template-russian.pptx",
    "1159194553.key": "templates/presentation/hse-template-russian.key",
    "1159194596.pptx": "templates/presentation/hse-template-english.pptx",
    "1159194671.key": "templates/presentation/hse-template-english.key",
    "HSE_brandbook_first_edition_V7_10.04.2026.pdf": "guidelines/HSE-brandbook-2026-04-10.pdf",
}


def is_metadata(path: PurePosixPath) -> bool:
    return any(
        part == "__MACOSX"
        or part == ".DS_Store"
        or part.startswith("._")
        for part in path.parts
    )


def safe_member_path(root: Path, member: str) -> Path | None:
    path = PurePosixPath(member)
    if path.is_absolute() or ".." in path.parts or is_metadata(path):
        return None
    target = root.joinpath(*path.parts)
    resolved_root = root.resolve()
    resolved_target = target.resolve()
    if resolved_target != resolved_root and resolved_root not in resolved_target.parents:
        raise ValueError(f"Unsafe archive member: {member}")
    return target


def crc32(path: Path) -> int:
    checksum = 0
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            checksum = zlib.crc32(chunk, checksum)
    return checksum & 0xFFFFFFFF


def extract_zip(
    archive: Path,
    destination: Path,
    recursive: bool = True,
    force: bool = False,
) -> int:
    extracted = 0
    nested: list[Path] = []
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        for item in package.infolist():
            target = safe_member_path(destination, item.filename)
            if target is None:
                continue
            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and not force:
                if target.stat().st_size != item.file_size or crc32(target) != item.CRC:
                    raise FileExistsError(f"Refusing to overwrite changed file: {target}")
            else:
                with package.open(item) as source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                extracted += 1
            if recursive and target.suffix.lower() == ".zip":
                nested.append(target)

    for archive_path in nested:
        nested_destination = archive_path.with_suffix("")
        extracted += extract_zip(
            archive_path,
            nested_destination,
            recursive=True,
            force=force,
        )
        archive_path.unlink()
    return extracted


def copy_file(source: Path, destination: Path, force: bool = False) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and not force:
        if filecmp.cmp(source, destination, shallow=False):
            return
        raise FileExistsError(f"Refusing to overwrite changed file: {destination}")
    shutil.copy2(source, destination)


def parse_args() -> argparse.Namespace:
    skill_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=skill_root / "assets" / "original-downloads",
        help="Folder containing the files downloaded from hse.ru",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=skill_root / "assets" / "official",
        help="Folder to receive normalized unpacked assets",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite changed files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = [name for name in (*ARCHIVES, *FILES) if not (args.source / name).is_file()]
    if missing:
        print("Missing source files:", file=sys.stderr)
        for name in missing:
            print(f"  - {name}", file=sys.stderr)
        return 2

    total = 0
    for filename, relative_destination in ARCHIVES.items():
        total += extract_zip(
            args.source / filename,
            args.destination / relative_destination,
            recursive=True,
            force=args.force,
        )

    for filename, relative_destination in FILES.items():
        copy_file(
            args.source / filename,
            args.destination / relative_destination,
            force=args.force,
        )
        total += 1

    print(f"Prepared {total} files in {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
