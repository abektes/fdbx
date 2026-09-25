import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_support import cited_claims  # noqa: E402
from conformance import enumerate_items, score_document  # noqa: E402


def spec(enumerators: dict, structural: list) -> dict:
    return {"enumerators": enumerators, "structural": structural, "semantic": []}


TIMELINE = """## Backward Timeline

| When | Event | Critical? | Control (1/2/3) |
|---|---|---|---|
| 2040 | Preferred future | Yes | — |
| 2035 | Standard adopted | Yes | 3 |
| 2030 | Pilots scale | Yes | 2 |
| Now | Today | — | — |
"""


class StructuralKindsTest(unittest.TestCase):
    def test_descending_years_passes_a_backward_timeline(self) -> None:
        s = spec({"when": {"type": "table_cells", "in_section": "backward timeline", "column": "when"}},
                 [{"id": "t", "kind": "descending_years", "items": "when", "desc": "", "bar": ""}])
        self.assertTrue(score_document(TIMELINE, s, None)["structural"][0]["passed"])

    def test_descending_years_fails_a_forward_timeline(self) -> None:
        forward = TIMELINE.replace("| 2040 |", "| 2025 |").replace("| 2030 |", "| 2041 |")
        s = spec({"when": {"type": "table_cells", "in_section": "backward timeline", "column": "when"}},
                 [{"id": "t", "kind": "descending_years", "items": "when", "desc": "", "bar": ""}])
        self.assertFalse(score_document(forward, s, None)["structural"][0]["passed"])

    def test_control_scores_skip_bookend_and_non_critical_rows(self) -> None:
        e = {"type": "table_cells", "in_section": "backward timeline", "column": "control",
             "skip_first": True, "where": {"column": "critical", "matches": "yes"}}
        self.assertEqual(enumerate_items(TIMELINE, e), ["3", "2"])

    def test_no_new_numbers_catches_an_invented_figure(self) -> None:
        doc = "## Scans\n\n| Signal | Evidence type |\n|---|---|\n| Footfall down 12% | user-supplied |\n"
        s = spec({"u": {"type": "table_cells", "in_section": "^scans$", "column": "signal"}},
                 [{"id": "n", "kind": "no_new_numbers", "items": "u", "desc": "", "bar": ""}])
        self.assertFalse(score_document(doc, s, None, prompt="footfall is down")["structural"][0]["passed"])
        self.assertTrue(score_document(doc, s, None, prompt="footfall is down 12%")["structural"][0]["passed"])


class BatchOneKindsTest(unittest.TestCase):
    def test_distinct_cells_counts_different_values(self) -> None:
        doc = "## Layer Table\n\n| Layer | Problem-solver |\n|---|---|\n| A | Team |\n| B | Team |\n| C | Council |\n"
        e = {"s": {"type": "table_cells", "in_section": "layer table", "column": "solver"}}
        three = spec(e, [{"id": "d", "kind": "distinct_cells", "items": "s", "n": 3, "desc": "", "bar": ""}])
        two = spec(e, [{"id": "d", "kind": "distinct_cells", "items": "s", "n": 2, "desc": "", "bar": ""}])
        self.assertFalse(score_document(doc, three, None)["structural"][0]["passed"])
        self.assertTrue(score_document(doc, two, None)["structural"][0]["passed"])

    def test_pattern_absent_ignores_a_line_that_states_the_rule(self) -> None:
        s = spec({}, [{"id": "r", "kind": "pattern_absent", "pattern": "most likely", "desc": "", "bar": ""}])
        self.assertTrue(score_document("No future is called most likely.", s, None)["structural"][0]["passed"])
        self.assertFalse(score_document("Growth is the most likely future.", s, None)["structural"][0]["passed"])

    def test_all_sections_collects_every_repeated_list(self) -> None:
        doc = ("## Future 1\n**D. Five things to do now toward:**\n1. a\n2. b\n"
               "## Future 2\n**D. Five things to do now toward (x, y):\n1. c\n")  # second label left unclosed
        e = {"type": "list_items", "in_section": "^D\\.\\s*five things", "all_sections": True}
        self.assertEqual(enumerate_items(doc, e), ["a", "b", "c"])

    def test_list_after_reads_bullets_under_an_inline_label(self) -> None:
        doc = "**Robust design decisions:** These hold everywhere.\n\n- Offline ledger\n- Portable identity\n\n**Single-future bets:**\n- X\n"
        self.assertEqual(enumerate_items(doc, {"type": "list_after", "label": "robust design decisions"}),
                         ["Offline ledger", "Portable identity"])

    def test_list_items_fall_back_to_sub_headings(self) -> None:
        doc = "## Scenarios\n\n### 1. Digital Accelerator\nText.\n\n### 2. Community Anchor\nText.\n\n## Next\n"
        self.assertEqual(len(enumerate_items(doc, {"type": "list_items", "in_section": "^scenarios"})), 2)


class EnumeratorOptionsTest(unittest.TestCase):
    def test_column_list_falls_back_to_second_name(self) -> None:
        doc = "## Scans\n\n| Signal | Type |\n|---|---|\n| A | sourced |\n"
        e = {"type": "table_cells", "in_section": "^scans$", "column": ["evidence", "type"]}
        self.assertEqual(enumerate_items(doc, e), ["sourced"])

    def test_with_columns_appends_the_source(self) -> None:
        doc = "## Scans\n\n| Signal | Source |\n|---|---|\n| A launched B | news.com |\n"
        e = {"type": "table_cells", "in_section": "^scans$", "column": "signal", "with_columns": ["source"]}
        self.assertEqual(enumerate_items(doc, e), ["A launched B\nSource: news.com"])

    def test_with_body_keeps_indented_recommendation(self) -> None:
        doc = ("## Drivers of Change\n\n1. **Anticipatory ordering**\n   *Recommendation:* prototype a consent flow.\n"
               "2. **Wellness first**\n   *Research need:* test labels.\n")
        items = enumerate_items(doc, {"type": "list_items", "in_section": "drivers", "with_body": True})
        self.assertEqual(len(items), 2)
        self.assertIn("prototype a consent flow", items[0])


class CitedClaimsTest(unittest.TestCase):
    def test_table_claim_is_the_signal_cell(self) -> None:
        doc = ("| # | Signal | Source |\n|---|---|---|\n"
               "| 1 | Roquette launched a foresight platform called Horizons | [site](https://x.com/a) |\n")
        self.assertEqual(cited_claims(doc), [("https://x.com/a", "Roquette launched a foresight platform called Horizons")])


if __name__ == "__main__":
    unittest.main()
