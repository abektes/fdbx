import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from check_links import MD_URL_RE, norm  # noqa: E402


class CheckLinksTest(unittest.TestCase):
    def test_markdown_url_keeps_inner_parentheses(self) -> None:
        text = "see [EP](https://www.europarl.europa.eu/doc/EPRS_BRI(2023)746128) now"
        self.assertEqual(MD_URL_RE.findall(text),
                         ["https://www.europarl.europa.eu/doc/EPRS_BRI(2023)746128"])

    def test_norm_ignores_scheme_www_slash_and_tracking(self) -> None:
        self.assertEqual(norm("https://www.Example.com/a/?utm_source=x"), norm("http://example.com/a"))


if __name__ == "__main__":
    unittest.main()
