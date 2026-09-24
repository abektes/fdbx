# fdbx Foundation and Batch 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up `fdbx`, a futures-thinking skill box built the edbx way, with its first four skills grounded in sources a reader can open and check.

**Architecture:** A new repo at `~/WDesignspace/fdbx` that mirrors edbx's layout (`fdbx/fdbx-*/SKILL.md`, `scripts/`, `tutorials/`, `skills/` symlinks, `.claude-plugin/`). The edbx harness is copied and parameterised through one file, `scripts/box.py`, so the same code can later serve edbx, fdbx and sdbx. Two things are new relative to edbx: a **provenance gate** (every source-attributed claim in a skill carries a page locator and an anchor phrase that a script finds in the downloaded source), and **shared output conventions** (every skill ends with an Evidence Ledger and a Handoff block).

**Tech Stack:** Markdown skills; Python 3.12 standard library only for scripts; `pdftotext` / `pdfinfo` (poppler) for source text; `unittest` for tests; OpenRouter + DeepSeek V4 Pro and TypeSafe Jev for evaluation, inherited from edbx.

## Global Constraints

- Nothing in `~/WDesignspace/Ethical-design-package` is modified. edbx files are read and copied, never edited.
- Scripts use the Python standard library only (plus the `pdftotext`/`pdfinfo` binaries in `fetch_sources.py`).
- Downloaded sources under `sources/` are never committed. Only `sources/manifest.json` and `sources/README.md` are tracked; `scripts/fetch_sources.py` rebuilds the library.
- Anchor phrases in provenance tables are 3–12 words. Skills paraphrase their sources; they do not copy passages.
- Every skill separates **what the source says** (cited, in provenance) from **fdbx adaptation** (labelled as such, not attributed to the author).
- Skill directories are named `fdbx-<method>`; frontmatter keys are limited to `name`, `description`, `version`, `tags`.
- Any paid API run (OpenRouter generation, TypeSafe scoring) happens only after the user approves a cost estimate padded 3–4× for long outputs.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Source library (downloaded 2026-09-24, user-approved)

| Key | Citation | Printed page = PDF page + offset |
|---|---|---|
| `inayatullah-1998-cla` | Inayatullah, S. (1998). Causal layered analysis: Poststructuralism as method. *Futures* 30(8), 815–829. Author-hosted full text (HTML, no page numbers → cite by section) | n/a (§ locators) |
| `inayatullah-2008-six-pillars` | Inayatullah, S. (2008). Six pillars: futures thinking for transforming. *Foresight* 10(1), 4–21 | +3 |
| `dator-2009-manoa` | Dator, J. (2009). Alternative futures at the Manoa School. *Journal of Futures Studies* 14(2), 1–18 | 0 |
| `sharpe-2016-three-horizons` | Sharpe, B., Hodgson, A., Leicester, G., Lyon, A., Fazey, I. (2016). Three horizons: a pathways practice for transformation. *Ecology and Society* 21(2):47 | 0 (no printed pages; cite PDF page) |
| `curry-hodgson-2008-horizons` | Curry, A., Hodgson, A. (2008). Seeing in multiple horizons: Connecting futures to strategy. *Journal of Futures Studies* 13(1), 1–20 | 0 |
| `go-science-2024-toolkit` | UK Government Office for Science (2024). *The Futures Toolkit*, 2nd ed. (OGL) | batch 2 |
| `glenn-2009-futures-wheel` | Glenn, J. C. (2009). The Futures Wheel. In *Futures Research Methodology 3.0*, Millennium Project | batch 2 |
| `bleecker-2009-design-fiction` | Bleecker, J. (2009). *Design Fiction: A short essay on design, science, fact and fiction*. Near Future Laboratory (CC BY-NC-ND 3.0) | batch 2 |
| `voros-2017-futures-cone` | Voros, J. (2017). The Futures Cone, use and history. *The Voroscope* (blog) | batch 2 |

Verified discrepancies to carry into the skills:
- Dator's third generic future is **"Discipline"** in Dator (2009, pp. 1, 10) and **"Steady state"** in Inayatullah's retelling (2008, p. 16). Cite Dator; note the alias.
- Dator's **Transformation** is technology-led, "posthuman" (2009, p. 10); Inayatullah adds a spiritual route (2008, pp. 16–17).
- The **futures** Three Horizons (Sharpe & Hodgson) has all three horizons co-existing; the **management** original (Baghai, Coley & White 1999, McKinsey) draws successive growth curves (Curry & Hodgson 2008, pp. 4–5). The skill must not produce the McKinsey version.

---

## File structure

```
~/WDesignspace/fdbx/
├── .gitignore                      sources/*, eval-framework/, .env, __pycache__
├── .claude-plugin/plugin.json      plugin id "fdbx"
├── .github/workflows/validate-skills.yml
├── LICENSE                         MIT, same holder as edbx
├── README.md                       what fdbx is, how to verify sources, skill index
├── SOURCES.md                      human bibliography + cite-only list + discrepancies
├── install-skills.sh
├── docs/
│   ├── conventions.md              Evidence Ledger + Handoff formats, adaptation labelling
│   └── superpowers/plans/…         this plan
├── sources/
│   ├── manifest.json               tracked: key → file, url, kind, page_offset, citation, licence
│   ├── README.md                   tracked: how to rebuild
│   └── (pdf/html/pages/)           untracked
├── scripts/
│   ├── box.py                      the only box-specific constants
│   ├── fetch_sources.py            download + per-page text extraction
│   ├── check_provenance.py         anchor-phrase gate
│   ├── validate_skills.py          ported from edbx + fdbx rules
│   ├── run_generation.py           ported (baseline role = futures and foresight)
│   ├── conformance.py, calibrate.py, scaffold_conformance.py,
│   ├── lint_template_gaps.py, compare_scores.py   ported, box-parameterised
├── tests/
│   ├── test_check_provenance.py
│   └── test_validate_skills.py
├── fdbx/
│   ├── fdbx/SKILL.md               router
│   ├── fdbx-causal-layered-analysis/{SKILL.md, references/provenance.md, references/…, assets/…, evals/evals.json}
│   ├── fdbx-futures-triangle/…
│   ├── fdbx-four-futures/…
│   └── fdbx-three-horizons/…
├── skills/                         symlinks: <short> -> ../fdbx/fdbx-<short>/
└── tutorials/{README.md, <short>.md ×4}
```

---

### Task 1: Repo scaffold and source manifest

**Files:**
- Create: `.gitignore`, `LICENSE`, `.claude-plugin/plugin.json`, `install-skills.sh`, `sources/manifest.json`, `sources/README.md`, `SOURCES.md`, `README.md` (stub)

**Interfaces:**
- Produces: `sources/manifest.json` — object keyed by source key; each value has `file`, `url`, `kind` (`"pdf"`|`"html"`), `page_offset` (int or null), `citation`, `licence`, and for HTML `text_start`/`text_end` markers.

- [ ] **Step 1:** `git init` in `~/WDesignspace/fdbx`, default branch `main`.
- [ ] **Step 2:** Write `.gitignore`:

```gitignore
# Downloaded sources are copyrighted; rebuild with scripts/fetch_sources.py
sources/*
!sources/manifest.json
!sources/README.md

# Evaluation outputs and secrets
eval-framework/
.env
*.env

__pycache__/
*.py[cod]
.DS_Store
.venv/
```

- [ ] **Step 3:** Write `sources/manifest.json` with the nine keys in the table above (URLs exactly as downloaded; see Task 2's fetch script for the fields it reads).
- [ ] **Step 4:** Copy `LICENSE` from edbx; write `plugin.json` (`"name": "fdbx"`), `install-skills.sh` (edbx's, with `edbx`→`fdbx`), `sources/README.md`, `SOURCES.md` (every manifest key + a "cite only, not downloaded" list: Robinson 1982/1990 backcasting, Voros 2003, Inayatullah 2023 futures triangle, Candy 2018, Dator 1996/2019 "What futures studies is and is not" + the discrepancies above).
- [ ] **Step 5: Verify ignore rules**

Run: `git check-ignore -v sources/dator-2009-manoa-alternative-futures.pdf && git check-ignore sources/manifest.json; echo "manifest ignored? exit=$?"`
Expected: first command prints the `sources/*` rule; second prints nothing and `exit=1` (manifest is tracked).

- [ ] **Step 6: Commit** `chore: scaffold fdbx repo and source manifest`

### Task 2: Source fetcher and provenance gate (TDD)

**Files:**
- Create: `scripts/box.py`, `scripts/fetch_sources.py`, `scripts/check_provenance.py`, `tests/test_check_provenance.py`

**Interfaces:**
- Consumes: `sources/manifest.json` (Task 1).
- Produces: `box.REPO, BOX, SKILLS_DIR, LINK_DIR, EVAL_DIR, SOURCES_DIR, MANIFEST, BASELINE_ROLE`, `box.short(name) -> str`, `box.evals_path(skill_name) -> Path`; `check_provenance.normalize(text) -> str`, `Row(line, source, locator, anchor)`, `parse_rows(md) -> list[Row]`, `check_row(row, manifest, sources_dir) -> str | None` (None = pass, else error message); per-page text at `sources/pages/<key>/NNN.txt`.

- [ ] **Step 1: Write `scripts/box.py`**

```python
"""The only box-specific constants. Every other script imports from here, so the
same harness can serve edbx, fdbx or sdbx by changing this one file."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BOX = "fdbx"
SKILLS_DIR = REPO / BOX
LINK_DIR = REPO / "skills"
EVAL_DIR = REPO / "eval-framework"
SOURCES_DIR = REPO / "sources"
MANIFEST = SOURCES_DIR / "manifest.json"
# Baseline arm's system prompt reads "You are an expert {BASELINE_ROLE} assistant."
BASELINE_ROLE = "futures and foresight"


def short(name: str) -> str:
    return name.removeprefix(f"{BOX}-")


def evals_path(skill_name: str) -> Path:
    """Eval scenarios are committed beside the skill. edbx kept them in the
    gitignored eval-framework/ tree, where they could be lost."""
    return SKILLS_DIR / skill_name / "evals" / "evals.json"
```

- [ ] **Step 2: Write the failing tests** `tests/test_check_provenance.py`

```python
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_provenance import Row, check_row, normalize, parse_rows  # noqa: E402


class CheckRowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        pages = self.tmp / "pages" / "dator"
        pages.mkdir(parents=True)
        (pages / "001.txt").write_text("Alternative Futures at the Manoa School")
        (pages / "007.txt").write_text("there is no such thing as either a “best\ncase scenario” or a")
        (pages / "008.txt").write_text("worse case scenario. Rationale for alternative future one")
        html = self.tmp / "pages" / "cla"
        html.mkdir(parents=True)
        (html / "001.txt").write_text("four levels: the litany, social causes, discourse/worldview and myth/metaphor")
        self.manifest = {
            "dator": {"kind": "pdf", "page_offset": 0},
            "shifted": {"kind": "pdf", "page_offset": 3},
            "cla": {"kind": "html", "page_offset": None},
        }
        shifted = self.tmp / "pages" / "shifted"
        shifted.mkdir(parents=True)
        (shifted / "004.txt").write_text("The futures triangle maps today's views of the future")

    def check(self, anchor: str, locator: str = "p. 7", source: str = "dator") -> str | None:
        return check_row(Row(1, source, locator, anchor), self.manifest, self.tmp)

    def test_anchor_on_cited_page_passes(self) -> None:
        self.assertIsNone(self.check("no such thing as either a best case"))

    def test_anchor_running_onto_next_page_passes(self) -> None:
        self.assertIsNone(self.check("case scenario or a worse case scenario"))

    def test_anchor_on_other_page_names_the_real_page(self) -> None:
        err = self.check("Alternative Futures at the Manoa", locator="p. 7")
        self.assertIsNotNone(err)
        self.assertIn("found on p. 1", err)

    def test_page_offset_maps_printed_page_to_pdf_page(self) -> None:
        self.assertIsNone(self.check("futures triangle maps today's views", locator="p. 7", source="shifted"))

    def test_section_locator_searches_whole_document(self) -> None:
        self.assertIsNone(self.check("social causes, discourse/worldview and myth/metaphor", locator="§ Abstract", source="cla"))

    def test_unknown_source_is_an_error(self) -> None:
        self.assertIn("unknown source", self.check("anything at all here", source="nope"))

    def test_anchor_length_is_bounded(self) -> None:
        self.assertIn("3-12 words", self.check("too short"))
        self.assertIn("3-12 words", self.check(" ".join(["word"] * 13)))

    def test_missing_text_tells_you_to_fetch(self) -> None:
        self.manifest["unfetched"] = {"kind": "pdf", "page_offset": 0}
        self.assertIn("fetch_sources.py", self.check("some anchor phrase here", source="unfetched"))


class ParseTest(unittest.TestCase):
    def test_reads_numbered_rows_only(self) -> None:
        md = (
            "| # | Skill element | Source | Locator | Anchor phrase | Note |\n"
            "|---|---|---|---|---|---|\n"
            "| 1 | Four layers | `cla` | § Abstract | litany, social causes | |\n"
            "| 2 | Equal probability | dator | p. 7 | “equal probabilities of happening” | |\n"
        )
        rows = parse_rows(md)
        self.assertEqual([(r.source, r.locator, r.anchor) for r in rows], [
            ("cla", "§ Abstract", "litany, social causes"),
            ("dator", "p. 7", "equal probabilities of happening"),
        ])

    def test_normalize_ignores_case_punctuation_and_line_breaks(self) -> None:
        self.assertEqual(normalize("Trans-\nformative “Change”"), normalize("transformative change"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest tests/test_check_provenance.py -v`
Expected: `ModuleNotFoundError: No module named 'check_provenance'`

- [ ] **Step 4: Write `scripts/check_provenance.py`**

```python
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
```

- [ ] **Step 5: Run tests to verify pass**

Run: `python3 -m unittest tests/test_check_provenance.py -v`
Expected: `Ran 10 tests … OK`

- [ ] **Step 6: Write `scripts/fetch_sources.py`**

```python
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
```

- [ ] **Step 7: Run it against the already-downloaded library**

Run: `python3 scripts/fetch_sources.py`
Expected: nine `✓` lines; `sources/pages/dator-2009-manoa/` holds `001.txt`…`018.txt`.

- [ ] **Step 8: Commit** `feat: source fetcher and provenance gate`

### Task 3: Port the edbx harness through `box.py`

**Files:**
- Create (copied from edbx, then edited): `scripts/validate_skills.py`, `scripts/run_generation.py`, `scripts/conformance.py`, `scripts/calibrate.py`, `scripts/scaffold_conformance.py`, `scripts/lint_template_gaps.py`, `scripts/compare_scores.py`, `.github/workflows/validate-skills.yml`
- Test: `tests/test_validate_skills.py`

**Interfaces:**
- Consumes: `box.*` (Task 2).
- Produces: `validate_skills.validate_skill(skill_dir: Path, rep: Report) -> None`, `validate_skills.Report` with `.errors`/`.warns` lists.

- [ ] **Step 1:** Copy the seven scripts from `~/WDesignspace/Ethical-design-package/scripts/` and the workflow file.
- [ ] **Step 2:** Replace every hardcoded box reference with `box` imports. The edit sites are exactly those listed by `grep -n 'edbx\|"eval-framework"\|evals.json' scripts/*.py`: `SKILLS_DIR = REPO / "edbx"` → `from box import …`; `removeprefix("edbx-")` → `short(...)`; `name == "edbx"` → `name == BOX`; `EVAL_DIR / name / "evals.json"` and `EVAL_DIR / skill / "evals.json"` → `evals_path(...)`; `REPO / "edbx" / …` → `SKILLS_DIR / …`; `f"edbx-{short}"` → `f"{BOX}-{short}"`. In `run_generation.py` the baseline prompt becomes `f"You are an expert {BASELINE_ROLE} assistant. Apply the {{method}} method thoroughly …"`.
- [ ] **Step 3: Verify no stray references**

Run: `grep -n 'edbx\|ethical design' scripts/*.py`
Expected: no output.

- [ ] **Step 4: Write the failing validator tests** `tests/test_validate_skills.py`

```python
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from validate_skills import Report, validate_skill  # noqa: E402

GOOD = """---
name: fdbx-demo
description: Demo skill.
version: "1.0"
tags: [futures]
---

# Demo

## Overview
x
## Use This Skill When
x
## Inputs
x
## Workflow
See `references/provenance.md`.
## Output Format
### Evidence Ledger
### Handoff
## Guardrails
x
## Deliverable Quality Bar
x
## Sources
x
"""


def make_skill(body: str, provenance: bool = True) -> Path:
    root = Path(tempfile.mkdtemp()) / "fdbx-demo"
    (root / "references").mkdir(parents=True)
    (root / "SKILL.md").write_text(body)
    if provenance:
        (root / "references" / "provenance.md").write_text("| 1 | a | b | c | d e f |\n")
    return root


class FdbxRulesTest(unittest.TestCase):
    def run_on(self, skill_dir: Path) -> Report:
        rep = Report()
        validate_skill(skill_dir, rep)
        return rep

    def test_complete_skill_is_clean(self) -> None:
        rep = self.run_on(make_skill(GOOD))
        self.assertEqual((rep.errors, rep.warns), ([], []))

    def test_missing_provenance_is_an_error(self) -> None:
        body = GOOD.replace("See `references/provenance.md`.", "x")
        rep = self.run_on(make_skill(body, provenance=False))
        self.assertTrue(any("provenance" in e for e in rep.errors))

    def test_missing_evidence_ledger_is_an_error(self) -> None:
        rep = self.run_on(make_skill(GOOD.replace("### Evidence Ledger\n", "")))
        self.assertTrue(any("Evidence Ledger" in e for e in rep.errors))

    def test_missing_handoff_is_an_error(self) -> None:
        rep = self.run_on(make_skill(GOOD.replace("### Handoff\n", "")))
        self.assertTrue(any("Handoff" in e for e in rep.errors))

    def test_missing_sources_section_warns(self) -> None:
        rep = self.run_on(make_skill(GOOD.replace("## Sources\nx\n", "")))
        self.assertTrue(any("Sources" in w for w in rep.warns))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Run to verify failure**

Run: `python3 -m unittest tests/test_validate_skills.py -v`
Expected: `test_complete_skill_is_clean` fails (a Sources warning), and the three error tests fail (no such rules yet).

- [ ] **Step 6: Add the fdbx rules to `validate_skills.py`**

Append `"Sources"` to `EXPECTED_SECTIONS`, and add this block at the end of `validate_skill`, after the heading check:

```python
    # fdbx rules. Routers dispatch rather than produce a deliverable, so they are exempt.
    if not is_router:
        if "references/provenance.md" not in linked:
            rep.error(name, "must link references/provenance.md (every sourced claim needs a locator)")
        for block in ("Evidence Ledger", "Handoff"):
            if block not in body:
                rep.error(name, f"output format must include a '{block}' block (see docs/conventions.md)")
```

- [ ] **Step 7: Run all tests**

Run: `python3 -m unittest discover -s tests -v`
Expected: all pass.

- [ ] **Step 8: Smoke-test the ported scripts**

Run: `python3 scripts/validate_skills.py; python3 scripts/run_generation.py --help >/dev/null && python3 scripts/conformance.py --help >/dev/null && echo ok`
Expected: `Checked 0 skills — clean.` then `ok`.

- [ ] **Step 9: Commit** `feat: port edbx harness, parameterised by box.py, with fdbx rules`

### Task 4: Conventions document

**Files:** Create `docs/conventions.md`

- [ ] **Step 1:** Write the conventions every non-router skill follows:
  - **Evidence Ledger** (output): table `| Claim used as input | Type | Basis |`, where Type is `user-supplied`, `sourced` (with link) or `assumption`. Futures signals, trends and statistics may never appear untyped. Anything the model knows from training is `assumption`.
  - **Handoff** (output): `Assumptions surfaced` (bullets), `Open decisions`, `Suggested next method` naming an fdbx or edbx skill and why.
  - **Adaptation labelling** (skill text): a `> **fdbx adaptation:**` callout marks every step the source does not describe, e.g. translating a layer into design-brief terms.
  - **Provenance table** columns: `| # | Skill element | Source | Locator | Anchor phrase | Note |`; locators are `p. N` (printed page) or `§ Heading` (HTML sources).
- [ ] **Step 2: Commit** `docs: output and provenance conventions`

### Task 5: Eval scenarios for batch 1

**Files:** Create `fdbx/fdbx-<skill>/evals/evals.json` for the four skills (directories created here).

- [ ] **Step 1:** Write three design-context scenarios per skill in edbx's `evals.json` shape (`skill_name`, `evals[] {id, name, prompt, expected_output, files}`). Scenarios name a real design situation (a brief, a product, a service) plus a horizon year, so outputs are comparable across arms.
- [ ] **Step 2: Verify JSON**

Run: `for f in fdbx/*/evals/evals.json; do python3 -m json.tool "$f" >/dev/null && echo "ok $f"; done`
Expected: four `ok` lines.

- [ ] **Step 3: Commit** `test: eval scenarios for batch 1`

### Tasks 6–9: The four skills

Each skill task has the same shape and the same acceptance gate. **Files** per skill: `fdbx/fdbx-<skill>/SKILL.md`, `references/provenance.md`, supporting `references/*.md` / `assets/*-template.md`, and `tutorials/<short>.md`.

Steps per skill:
- [ ] **Step 1:** Write `references/provenance.md` first: one row per source-attributed element listed below, anchors verified by hand against the page text.
- [ ] **Step 2: Run the gate before writing the skill**

Run: `python3 scripts/check_provenance.py --skills <short>`
Expected: `Checked N anchors — 0 problem(s).`

- [ ] **Step 3:** Write `SKILL.md` in edbx house style (Overview, Use This Skill When, Inputs, Workflow, Output Format incl. Evidence Ledger + Handoff, Guardrails, Deliverable Quality Bar, Integration, Sources). Paraphrase; mark adaptations.
- [ ] **Step 4:** Write the tutorial (edbx tutorial shape: what it does, when, what you get, key insight, worked example).
- [ ] **Step 5: Run the gates**

Run: `python3 scripts/validate_skills.py --strict && python3 scripts/check_provenance.py --skills <short>`
Expected: clean validator, `0 problem(s)`.

- [ ] **Step 6: Commit** `feat(<short>): <method> skill with page-cited provenance`

**Task 6 — `fdbx-causal-layered-analysis`** (sources: `inayatullah-1998-cla`, `inayatullah-2008-six-pillars` pp. 12–14)
Source-attributed elements: premise that framing a problem changes the solution and who acts; the four layers (litany; social causes; discourse/worldview, actor-invariant structures; myth/metaphor, deep story in evocative language); the Appendix's four columns per layer (problem, solution, problem-solver, where it appears); who solves at each layer (others/government → partnerships → people/voluntary associations → leaders or artists); scenarios differ in kind per layer; move back up from the deeper layers to reach wiser action; don't debate what belongs where; limits (doesn't forecast; risk of paralysis; best before scenario building, with visioning/backcasting).
fdbx adaptation: read a design brief as the litany; the output shows what the brief assumes at each layer and a brief rewritten from an alternative metaphor.

**Task 7 — `fdbx-futures-triangle`** (source: `inayatullah-2008-six-pillars` pp. 7–8, 15)
Source-attributed elements: pull of images of the future, with five archetypes (evolution and progress; collapse; Gaia; globalism; back to the future); push of the present as quantitative drivers and trends; weight as barriers, which differ per image; the interaction of the three helps develop a plausible future; multi-single-variable scenarios derived from the triangle.
fdbx adaptation: pushes must be typed in the Evidence Ledger; the output names which image the current product strategy is silently serving.

**Task 8 — `fdbx-four-futures`** (source: `dator-2009-manoa`; alias note from `inayatullah-2008-six-pillars` p. 16)
Source-attributed elements: the four generic futures (continued growth, collapse, discipline, transformation) and each one's rationale; no best/worst/most-likely future, equal long-run probability, all presented positively; the four differ fundamentally, not as variations of shared variables; always at least one of each, more allowed; exercise questions A–E (life in that future, probability, preferability, five moves toward, five moves against); goals, including questioning "the present extended"; artifacts from the future; 20–50-year default horizon; the exercise sits inside a seven-part visioning process.
fdbx adaptation: place the user's product or service in each future and ask how it would thrive there; produce one artifact per future; list design decisions that hold up in all four.

**Task 9 — `fdbx-three-horizons`** (sources: `sharpe-2016-three-horizons`, `curry-hodgson-2008-horizons`)
Source-attributed elements: H1 (business as usual, losing fit), H3 (emerging successor, visible as pockets of the future in the present), H2 (turbulent transition); horizons co-exist rather than succeed each other; H2+ vs H2− innovations; the five steps (present concerns → future aspirations → inspirational practice → innovations in play → features to maintain); manager / entrepreneur / visionary mindsets, and each horizon's negative mindset vs positive perspective on the others; dilemma thinking for H2; power (who can influence change); horizon length varies by domain; origin in Baghai et al. 1999 and how the futures version differs; the paper presents itself as practice propositions, not tested effectiveness.
fdbx adaptation: map a product or service portfolio; classify each current initiative as H1 / H2+ / H2− / H3.

### Task 10: Router, README, tutorials index, symlinks

**Files:** Create `fdbx/fdbx/SKILL.md` (tags `[futures, router]`), `skills/<short>` symlinks, `tutorials/README.md`; finish `README.md`.

- [ ] **Step 1:** Router table by situation: "the brief feels obvious" → CLA; "what forces shape this?" → futures triangle; "we assume one future" → four futures; "how do we get from today's model to the next?" → three horizons. Chains: triangle → four futures → three horizons; CLA before any scenario work (CLA 1998). Cross-box: a chosen future → `edbx:worrystorming` / `edbx:black-mirror-brainstorming` / `edbx:stf-et`.
- [ ] **Step 2:** `ln -s ../fdbx/fdbx-<short>/ skills/<short>` for each skill, plus `skills/help -> ../fdbx/fdbx/`.
- [ ] **Step 3: Full gate**

Run: `python3 -m unittest discover -s tests && python3 scripts/validate_skills.py --strict && python3 scripts/check_provenance.py`
Expected: tests OK; `Checked 5 skills — clean.`; `0 problem(s)`.

- [ ] **Step 4: Commit** `feat: fdbx router, README and tutorial index`

### Task 11 (gated on user approval of spend): baseline probe and A/B

- [ ] **Step 1:** Estimate: 4 skills × 3 scenarios × 3 reps × 2 arms = 72 generations. Price at OpenRouter's current DeepSeek V4 Pro rate, assuming 8k output tokens each, ×4 padding. Show the figure; wait for approval.
- [ ] **Step 2:** `python3 scripts/run_generation.py --reps 3` (baseline arm first: `--arms without_skill`) and read the baseline outputs for the failure modes the skills target: McKinsey horizons, a "most likely" future, CLA stopping at the systemic layer, untyped trend claims.
- [ ] **Step 3:** Write findings to `docs/baseline-probe-batch-1.md`; revise the skills where the probe shows a gap; add `conformance.json` rubrics and calibrate them (separate plan).

---

## Execution notes (2026-09-24)

Tasks 1–10 were executed inline. Deviations from the plan as written:

- **No commits yet.** Commits happen only when the user asks, so every task's commit step is pending. The repo is initialised on `main` with all work untracked.
- **Task 3, Step 3:** `grep 'edbx'` still matches three docstrings that record edbx history on purpose. No hardcoded paths remain.
- **Tasks 6–10, "clean" validator:** `validate_skills.py` reports 0 errors and 5 warnings. The warnings are the `skills/` symlink names, which edbx has too (32 warnings there) because the plugin invokes skills by short name. `--strict` therefore exits non-zero in both repos.
- **Added:** `lint_template_gaps.py` found five quality-bar items with no output-format slot; all five were fixed (0 gaps).
- **Added:** negative controls on real sources confirm the provenance gate rejects a wrong page (and names the right one), fabricated claims, swapped names, and McKinsey-style wording.
- **Corrections made while writing:** the Glenn chapter's page offset is −3, not +1; unsourced claims were removed or reworded in two tutorials; "AI tools mix up the two Three Horizons" is now stated as a hypothesis for the probe.

**Task 11 cost estimate.** From edbx's 558 cached generations (DeepSeek V4 Pro via OpenRouter): median $0.015, p90 $0.033, max $0.070 per generation. 72 generations × $0.033 ≈ $2.40; padded 4× ≈ **$9.50**. A baseline-only probe (36 generations) is about $1.20, padded ≈ **$5**. TypeSafe scoring is extra and needs rubrics first.

**Task 11 done (2026-09-24).** Baseline arm $0.39, with-skill arm $0.76, both via OpenRouter DeepSeek V4 Pro. Findings and one skill defect (ledger evidence types), with its fix and a new validator rule, are in `docs/baseline-probe-batch-1.md`. Re-run of the three changed skills done ($0.59): correctly typed ledger rows went from 0–41% to 98–100%. Total probe spend $1.74.

## Next plan (not in scope here)

- Divergence evaluation: distance from the baseline's cliché set, spread across reps, and a small blind practitioner review.
- Batch 2 skills from the already-downloaded library: futures wheel (Glenn), futures cone (Voros), backcasting (GO-Science toolkit), design fiction (Bleecker), signal scanning (GO-Science toolkit). **Done (2026-09-24):** all five probed; backcasting and horizon scanning written, the other three kept in `candidates/`. See `docs/baseline-probe-batch-2.md`.
- Extract `scripts/` into a shared package once edbx and fdbx both need the same change.
