#!/usr/bin/env python3
"""Download every source in sources/manifest.json and extract per-page text.

The PDFs are copyrighted, so the repo tracks only the manifest. This script
rebuilds the local library; check_provenance.py reads the page text it writes.

    python3 scripts/fetch_sources.py            # fetch what is missing, re-extract text
    python3 scripts/fetch_sources.py --force    # re-download everything
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

from box import MANIFEST, SOURCES_DIR

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) fdbx-fetch/1.0"


def download(url: str, dest: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=90) as response:
        dest.write_bytes(response.read())


def html_to_text(raw: str, start: str | None, end: str | None) -> str:
    raw = re.sub(r"<script.*?</script>|<style.*?</style>", "", raw, flags=re.S)
    raw = re.sub(r"</(p|h\d|li|div|td|tr)>|<br\s*/?>", "\n", raw)
    text = html.unescape(re.sub(r"<[^>]+>", "", raw))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    if start and (i := text.find(start)) >= 0:
        text = text[i:]
    if end and (j := text.find(end)) >= 0:
        text = text[:j]
    return text.strip()


def extract(key: str, entry: dict) -> int:
    src = SOURCES_DIR / entry["file"]
    pages = SOURCES_DIR / "pages" / key
    pages.mkdir(parents=True, exist_ok=True)
    if entry["kind"] == "pdf":
        info = subprocess.run(["pdfinfo", str(src)], capture_output=True, text=True, check=True).stdout
        count = int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))
        for n in range(1, count + 1):
            out = subprocess.run(["pdftotext", "-f", str(n), "-l", str(n), str(src), "-"],
                                 capture_output=True, text=True, check=True).stdout
            (pages / f"{n:03d}.txt").write_text(out)
        return count
    raw = src.read_text(encoding="utf-8", errors="ignore")
    (pages / "001.txt").write_text(html_to_text(raw, entry.get("text_start"), entry.get("text_end")))
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    failed = 0
    for key, entry in manifest.items():
        dest = SOURCES_DIR / entry["file"]
        try:
            if args.force or not dest.is_file():
                download(entry["url"], dest)
            n = extract(key, entry)
            print(f"  ✓ {key:34s} {n:>4} page(s)")
        except Exception as exc:  # noqa: BLE001 - report and continue with the rest
            failed += 1
            print(f"  ✗ {key:34s} {exc}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
