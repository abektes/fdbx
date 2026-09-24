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
