import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def body(path: Path) -> str:
    text = path.read_text()
    text = text.split("---", 2)[2]  # drop frontmatter
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return text.strip()


class AgentTest(unittest.TestCase):
    def test_plugin_agent_matches_agent_md(self) -> None:
        # AGENT.md is read by any AI tool pointed at the repo; agents/ is what the
        # Claude Code plugin loads. They must say the same thing.
        self.assertEqual(body(REPO / "AGENT.md"), body(REPO / "agents" / "futures-design-specialist.md"))

    def test_agent_names_every_skill(self) -> None:
        agent = (REPO / "AGENT.md").read_text()
        skills = [p.name for p in (REPO / "skills").iterdir() if p.name != "help"]
        for name in skills:
            self.assertIn(f"/fdbx:{name}", agent, name)

    def test_marketplace_and_plugin_agree(self) -> None:
        plugin = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text())
        market = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text())
        entry = next(p for p in market["plugins"] if p["name"] == plugin["name"])
        self.assertEqual(entry["version"], plugin["version"])
        self.assertEqual(entry["source"], "./")


if __name__ == "__main__":
    unittest.main()
