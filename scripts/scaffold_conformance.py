#!/usr/bin/env python3
"""Scaffold and audit conformance specs against each skill's Deliverable Quality Bar.

Every check in a conformance.json carries a `bar` field quoting the criterion it
implements. This reads the Deliverable Quality Bar out of SKILL.md and reports
which bars are actually covered, so a partial rubric reports as partial instead of
quietly scoring a skill on the third of its bar that was easy to automate.

    python3 scripts/scaffold_conformance.py                 # coverage report
    python3 scripts/scaffold_conformance.py --init cider    # write a skeleton
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

from box import BOX, REPO, SKILLS_DIR, short  # noqa: F401


def quality_bars(skill_dir: Path) -> list[str]:
    """The bullet list under '## Deliverable Quality Bar', ignoring code fences."""
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    bars: list[str] = []
    in_section = in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            in_section = line[3:].strip().endswith("Deliverable Quality Bar")
            continue
        if in_section and line.strip().startswith(("-", "*")):
            bar = re.sub(r"[*`]+", "", line.strip().lstrip("-*").strip())
            if bar:
                bars.append(bar)
    return bars


def covered(bar: str, claims: list[str]) -> bool:
    """Does any check claim this bar? Fuzzy, since checks abbreviate the wording."""
    target = re.sub(r"[^a-z0-9 ]+", " ", bar.lower())
    for claim in claims:
        c = re.sub(r"[^a-z0-9 ]+", " ", claim.lower())
        if difflib.SequenceMatcher(None, target[:120], c[:120]).ratio() > 0.55:
            return True
        # A check may quote a distinctive fragment rather than the whole bar.
        if len(c) > 25 and c[:60] in target:
            return True
    return False


def audit() -> int:
    rows = []
    for skill_dir in sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir()):
        if skill_dir.name == BOX:
            continue
        bars = quality_bars(skill_dir)
        spec_path = skill_dir / "conformance.json"
        if not spec_path.is_file():
            rows.append((skill_dir.name, len(bars), 0, []))
            continue
        spec = json.loads(spec_path.read_text())
        claims = [c.get("bar", "") for c in spec.get("structural", []) + spec.get("semantic", [])]
        uncovered = [b for b in bars if not covered(b, claims)]
        rows.append((skill_dir.name, len(bars), len(bars) - len(uncovered), uncovered))

    total_bars = sum(r[1] for r in rows)
    total_cov = sum(r[2] for r in rows)

    print(f"{'skill':34s} {'bars':>5} {'covered':>8}  status")
    print("-" * 78)
    for name, n_bars, n_cov, _ in rows:
        pct = f"{100 * n_cov / n_bars:.0f}%" if n_bars else "-"
        status = "no spec" if n_cov == 0 else "complete" if n_cov == n_bars else "partial"
        print(f"{short(name):34s} {n_bars:>5} {n_cov:>8}  {status} ({pct})")
    print("-" * 78)
    print(f"{'TOTAL':34s} {total_bars:>5} {total_cov:>8}  "
          f"{100 * total_cov / total_bars:.0f}% of all quality bars are machine-checked")

    detail = [(n, u) for n, _, _, u in rows if u and (skill_dir / "conformance.json")]
    for name, uncovered in detail:
        if (SKILLS_DIR / name / "conformance.json").is_file():
            print(f"\n{short(name)} — bars not yet checked:")
            for bar in uncovered:
                print(f"  - {bar[:100]}")
    return 0


def init(short: str) -> int:
    skill_dir = SKILLS_DIR / f"{BOX}-{short}"
    if not skill_dir.is_dir():
        sys.exit(f"no such skill: {skill_dir}")
    path = skill_dir / "conformance.json"
    if path.is_file():
        sys.exit(f"{path} already exists")

    bars = quality_bars(skill_dir)
    skeleton = {
        "skill": skill_dir.name,
        "_note": "SKELETON — every check below is a placeholder. Verify each against real "
                 "generated output and against a baseline negative control before trusting "
                 "any number this produces.",
        "enumerators": {},
        "structural": [],
        "semantic": [],
        "_unimplemented_bars": bars,
    }
    path.write_text(json.dumps(skeleton, indent=2) + "\n")
    print(f"wrote {path.relative_to(REPO)} with {len(bars)} bars to implement")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--init", metavar="SKILL", help="write a skeleton spec for a skill")
    args = parser.parse_args()
    return init(args.init) if args.init else audit()


if __name__ == "__main__":
    sys.exit(main())
