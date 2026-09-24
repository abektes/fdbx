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
Type is `user-supplied`, `sourced` or `assumption`.
A `sourced` link comes from the user or a search in this session.
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

    def test_ledger_must_name_the_three_evidence_types(self) -> None:
        body = GOOD.replace("Type is `user-supplied`, `sourced` or `assumption`.\n", "")
        rep = self.run_on(make_skill(body))
        self.assertTrue(any("evidence types" in e for e in rep.errors))

    def test_ledger_must_say_where_sourced_links_come_from(self) -> None:
        body = GOOD.replace("A `sourced` link comes from the user or a search in this session.\n", "")
        rep = self.run_on(make_skill(body))
        self.assertTrue(any("in this session" in e for e in rep.errors))

    def test_missing_sources_section_warns(self) -> None:
        rep = self.run_on(make_skill(GOOD.replace("## Sources\nx\n", "")))
        self.assertTrue(any("Sources" in w for w in rep.warns))


if __name__ == "__main__":
    unittest.main()
