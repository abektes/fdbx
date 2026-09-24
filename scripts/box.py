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
