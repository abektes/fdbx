#!/usr/bin/env python3
"""Flag quality-bar requirements that the skill's own output template never asks for.

Both real defects found in the first improvement round had this shape. dah-cards
required a microcopy rewrite for every Unethical finding but placed the requirement
inside the optional Manifesto mode, with no slot in the Output Format; stf-et
required a scope declaration but told single-tool runs to output "only that tool's
section". A model fills in the template it is given, so a requirement with no slot
is a requirement that gets dropped.

This is triage, not a verdict. For each bar it measures what share of the bar's
substantive words appear anywhere in the Output Format section, and reports bars
below half. It catches missing slots; it cannot catch the stf-et kind of defect,
where the slot exists but another instruction suppresses it, and it is noisy on
behavioural bars ("works for teams of 2 to 20+") that need no slot at all. Each
hit still needs a conformance check against real output before anything is
edited. Word overlap with generated outputs was tried as that check and rejected:
a correct output never uses the words that describe a behavioural bar.

Validated against the known case: the pre-fix dah-cards microcopy bar scores 33%
and is flagged; after the fix it scores 67% and is not.

    python3 scripts/lint_template_gaps.py
    python3 scripts/lint_template_gaps.py --skills cider,fair-patterns
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from box import BOX, REPO, SKILLS_DIR, short as short_name  # noqa: F401

# Words that appear in bars as grammar rather than as named artifacts.
GENERIC = {
    "every", "each", "least", "session", "specific", "concrete", "named", "names",
    "produces", "includes", "provides", "identifies", "the", "a", "an", "and", "or",
    "not", "with", "for", "of", "to", "in", "on", "at", "by", "is", "are", "be",
    "that", "this", "it", "as", "when", "any", "all", "one", "two", "three", "user",
    "team", "design", "product", "Deliverable", "Quality", "Bar", "Mode", "Step",
}


def section(text: str, title_suffix: str) -> str:
    out, inside, fence = [], False, False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            inside = line[3:].strip().lower().endswith(title_suffix.lower())
            continue
        if inside:
            out.append(line)
    return "\n".join(out)


def bars(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", l.strip().lstrip("-*").strip())
            for l in section(text, "Deliverable Quality Bar").splitlines()
            if l.strip().startswith(("-", "*"))]


def stem(word: str) -> str:
    word = word.lower()
    for suffix in ("ings", "ing", "ies", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def content_words(text: str) -> set[str]:
    return {stem(w) for w in re.findall(r"[A-Za-z][A-Za-z-]{4,}", text)
            if w.lower() not in {g.lower() for g in GENERIC}}


def coverage(bar: str, template: str) -> tuple[float, list[str]]:
    """Share of the bar's substantive words that the template mentions anywhere.

    The first version extracted only capitalized and bolded terms, and missed the
    very defect it was written for: dah-cards' microcopy bar is anchored by the
    lowercase word "microcopy", while its one capitalized word, "Unethical", does
    appear in the template -- so the bar looked covered when it was not.
    """
    words = content_words(bar)
    if not words:
        return 1.0, []
    tpl = content_words(template)
    missing = sorted(w for w in words if w not in tpl)
    return 1 - len(missing) / len(words), missing


THRESHOLD = 0.5


def template_text(skill_dir: Path, text: str) -> str:
    """The Output Format section plus any template kept under assets/.

    Four skills keep their fill-in template in assets/*-template.md rather than in
    an Output Format section; ignoring those would report every bar as unanchored.
    """
    parts = [section(text, "Output Format")]
    for asset in sorted((skill_dir / "assets").glob("*.md")):
        if re.search(r"template|worksheet", asset.name, re.I):
            parts.append(asset.read_text(encoding="utf-8"))
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills")
    args = parser.parse_args()
    wanted = {s.strip() for s in args.skills.split(",")} if args.skills else None

    total = 0
    for skill_dir in sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir()):
        short = short_name(skill_dir.name)
        if skill_dir.name == BOX or (wanted and short not in wanted):
            continue
        text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        template = template_text(skill_dir, text).lower()
        if not template.strip():
            print(f"\n{short}: NO output template found -- every bar is unanchored")
            continue
        gaps = []
        for bar in bars(text):
            share, missing = coverage(bar, template)
            if share < THRESHOLD:
                gaps.append((share, bar, missing))
        if gaps:
            print(f"\n{short}")
            for share, bar, missing in sorted(gaps):
                total += 1
                print(f"  {share:4.0%}  {bar[:104]}")
                print(f"        absent from template: {', '.join(missing[:6])}")
    print(f"\n{total} bar(s) whose named artifact never appears in the output template")
    return 0


if __name__ == "__main__":
    sys.exit(main())
