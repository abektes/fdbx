#!/usr/bin/env python3
"""Check that every claim a skill attributes to a source can be found there.

Each skill keeps references/provenance.md: a table whose rows name a source key
from sources/manifest.json, a locator, and a short anchor phrase from the
source. This script confirms the anchor appears in that source -- on the cited
page when the locator is a printed page number -- so a reader can open the PDF
at that page and see the basis for the claim.

Matching ignores case, punctuation, whitespace and hyphenation, because PDF text
breaks lines and columns unpredictably. Anchors are therefore 3-12 words: long
enough to be unambiguous, short enough to be a pointer rather than a copy.

    python3 scripts/check_provenance.py
    python3 scripts/check_provenance.py --skills four-futures,three-horizons
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from box import BOX, MANIFEST, REPO, SKILLS_DIR, SOURCES_DIR, short

MIN_WORDS, MAX_WORDS = 3, 12
PAGE_RE = re.compile(r"^pp?\.\s*(\d+)")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).lower()
    return re.sub(r"[^a-z0-9]", "", text)


@dataclass
class Row:
    line: int
    source: str
    locator: str
    anchor: str


def parse_rows(md: str) -> list[Row]:
    """Rows whose first cell is a number: | # | element | source | locator | anchor | ... |"""
    rows: list[Row] = []
    for lineno, line in enumerate(md.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[0].isdigit():
            continue
        rows.append(Row(lineno, cells[2].strip("`"), cells[3], cells[4].strip("\"“”")))
    return rows


def load_pages(sources_dir: Path, key: str) -> dict[int, str]:
    folder = sources_dir / "pages" / key
    return {int(p.stem): normalize(p.read_text(errors="ignore")) for p in sorted(folder.glob("*.txt"))}


def check_row(row: Row, manifest: dict, sources_dir: Path) -> str | None:
    words = row.anchor.split()
    if not MIN_WORDS <= len(words) <= MAX_WORDS:
        return f"anchor must be {MIN_WORDS}-{MAX_WORDS} words, got {len(words)}"
    if row.source not in manifest:
        return f"unknown source {row.source!r} (not in sources/manifest.json)"
    pages = load_pages(sources_dir, row.source)
    if not pages:
        return f"no extracted text for {row.source!r}; run scripts/fetch_sources.py"
    needle = normalize(row.anchor)
    offset = manifest[row.source].get("page_offset")
    match = PAGE_RE.match(row.locator)
    if match and offset is not None:
        first = int(match.group(1)) - offset
        # An anchor may run from the foot of one page onto the next.
        if needle in pages.get(first, "") + pages.get(first + 1, ""):
            return None
        found = [n + offset for n, text in pages.items() if needle in text]
        where = f"; found on p. {', '.join(map(str, found))}" if found else ""
        return f"anchor not on {row.locator}{where}"
    if any(needle in text for text in pages.values()):
        return None
    return "anchor not found in source"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills", help="comma-separated short names")
    args = parser.parse_args()
    wanted = set(args.skills.split(",")) if args.skills else None

    manifest = json.loads(MANIFEST.read_text())
    sources_md = (REPO / "SOURCES.md").read_text()
    errors = [f"SOURCES.md: manifest key {k!r} is not listed" for k in manifest if k not in sources_md]

    checked = 0
    for skill_dir in sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and d.name != BOX):
        if wanted and short(skill_dir.name) not in wanted:
            continue
        prov = skill_dir / "references" / "provenance.md"
        if not prov.is_file():
            errors.append(f"{skill_dir.name}: no references/provenance.md")
            continue
        rows = parse_rows(prov.read_text())
        if not rows:
            errors.append(f"{skill_dir.name}: provenance.md has no numbered rows")
        for row in rows:
            checked += 1
            if (err := check_row(row, manifest, SOURCES_DIR)) is not None:
                errors.append(f"{skill_dir.name}/references/provenance.md:{row.line}: {err}")

    for line in errors:
        print(f"  ✗ {line}")
    print(f"\nChecked {checked} anchors — {len(errors)} problem(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
