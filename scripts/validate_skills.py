#!/usr/bin/env python3
"""Validate every fdbx SKILL.md before it ships.

Runs with no third-party dependencies so CI and a bare checkout behave the same.
If PyYAML happens to be importable it is used as a second opinion on the
frontmatter, but the hand-rolled parser below is the one that gates.

Severities:
  ERROR  breaks skill loading or leaves a dead link. CI fails.
  WARN   budget and consistency debt. Reported, does not fail CI.

    python3 scripts/validate_skills.py            # report
    python3 scripts/validate_skills.py --strict   # treat warnings as errors
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from box import BOX, LINK_DIR, SKILLS_DIR  # noqa: F401 - BOX used in messages

# Frontmatter keys we expect. Anything else is reported so a typo or a stray
# key from a refactor cannot sit unnoticed.
REQUIRED_KEYS = {"name", "description"}
KNOWN_KEYS = {"name", "description", "version", "tags"}

MAX_FRONTMATTER = 1024  # agentskills.io spec
NAME_RE = re.compile(r"^[a-z0-9-]+$")

# House style. Skills that predate it are reported as WARN, not ERROR.
# A heading satisfies an entry if it ends with it, so a meaningful qualifier like
# stf-et's "Chainable Workflow" counts as "Workflow" without being renamed flat.
# "Deliverable Quality Bar" is load-bearing: the conformance layer parses that
# section to build each skill's rubric, so a skill missing it cannot be scored.
EXPECTED_SECTIONS = [
    "Overview",
    "Use This Skill When",
    "Inputs",
    "Workflow",
    "Guardrails",
    "Deliverable Quality Bar",
    "Sources",
]

# Markdown/inline links to repo-relative paths, e.g. `references/foo.md` or [x](assets/y.md)
REL_PATH_RE = re.compile(r"(?:\(|`)((?:references|assets)/[^)`\s]+)(?:\)|`)")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warns: list[str] = []

    def error(self, skill: str, msg: str) -> None:
        self.errors.append(f"{skill}: {msg}")

    def warn(self, skill: str, msg: str) -> None:
        self.warns.append(f"{skill}: {msg}")


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Return (frontmatter, body). Frontmatter is None when absent or unterminated."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, text
    return text[4:end], text[end + 5 :]


def parse_frontmatter(fm: str) -> tuple[dict[str, str], list[str]]:
    """Strictly parse the flat `key: value` subset the skill spec allows.

    Returns (mapping, problems). This deliberately rejects the indented-key
    shape that silently broke edbx's stf-et skill, where `source:`/`license:` were left
    indented under `tags:` after their parent key was deleted.
    """
    data: dict[str, str] = {}
    problems: list[str] = []
    for lineno, raw in enumerate(fm.split("\n"), start=2):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] in " \t":
            problems.append(
                f"line {lineno}: unexpected indentation — "
                f"{raw.strip()[:60]!r} is nested under the previous key, "
                f"which is invalid for a flat scalar/flow value"
            )
            continue
        if ":" not in raw:
            problems.append(f"line {lineno}: not a `key: value` pair — {raw.strip()[:60]!r}")
            continue
        key, _, value = raw.partition(":")
        key = key.strip()
        if key in data:
            problems.append(f"line {lineno}: duplicate key {key!r}")
        data[key] = value.strip()
    return data, problems


def h2_headings(body: str) -> list[str]:
    """Real `## ` headings, ignoring anything inside a fenced code block.

    Output-format templates are fenced and full of `## Episode 1`-style lines that
    are illustrative, not structural. The conformance layer needs the same
    distinction when it locates a skill's Deliverable Quality Bar.
    """
    headings: list[str] = []
    in_fence = False
    for line in body.split("\n"):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and line.startswith("## "):
            headings.append(line[3:].strip())
    return headings


def cross_check_with_pyyaml(fm: str) -> str | None:
    """Second opinion, when available. Returns an error string or None."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return None
    try:
        yaml.safe_load(fm)
    except Exception as exc:  # noqa: BLE001 - surfacing the parser's own message
        return str(exc).split("\n")[0]
    return None


def validate_skill(skill_dir: Path, rep: Report) -> None:
    name = skill_dir.name
    path = skill_dir / "SKILL.md"

    if not path.is_file():
        rep.error(name, "no SKILL.md")
        return

    text = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)

    if fm is None:
        rep.error(name, "missing or unterminated `---` frontmatter block")
        return

    data, problems = parse_frontmatter(fm)
    for problem in problems:
        rep.error(name, f"frontmatter {problem}")

    if (yaml_err := cross_check_with_pyyaml(fm)) is not None:
        rep.error(name, f"frontmatter fails YAML parse: {yaml_err}")

    for key in sorted(REQUIRED_KEYS - data.keys()):
        rep.error(name, f"frontmatter missing required key {key!r}")

    for key in sorted(data.keys() - KNOWN_KEYS):
        rep.warn(name, f"frontmatter has unrecognized key {key!r}")

    declared = data.get("name", "")
    if declared and declared != name:
        rep.error(name, f"frontmatter name {declared!r} does not match directory {name!r}")
    if declared and not NAME_RE.match(declared):
        rep.error(name, f"name {declared!r} must be lowercase letters, numbers and hyphens only")

    if not data.get("description", "").strip():
        rep.error(name, "description is empty")

    if len(fm) > MAX_FRONTMATTER:
        rep.warn(name, f"frontmatter is {len(fm)} chars, over the {MAX_FRONTMATTER} limit")

    # Every support file must be reachable, and every link must resolve.
    linked = {m.group(1) for m in REL_PATH_RE.finditer(text)}
    for rel in sorted(linked):
        if not (skill_dir / rel).is_file():
            rep.error(name, f"links {rel} but that file does not exist")

    on_disk = {
        str(p.relative_to(skill_dir))
        for sub in ("references", "assets")
        for p in (skill_dir / sub).glob("*")
        if p.is_file() and p.name != ".DS_Store"
    }
    for orphan in sorted(on_disk - linked):
        rep.warn(name, f"{orphan} exists but is never linked from SKILL.md")

    # A router dispatches to methods rather than producing a deliverable of its
    # own, so the method-shaped sections do not apply to it.
    is_router = "router" in data.get("tags", "")
    router_exempt = {"Deliverable Quality Bar", "Sources"}
    expected = [s for s in EXPECTED_SECTIONS if not (is_router and s in router_exempt)]

    headings = h2_headings(body)
    for section in expected:
        if not any(h == section or h.endswith(f" {section}") for h in headings):
            rep.warn(name, f"missing house-style section '## {section}'")

    # fdbx rules. Routers dispatch rather than produce a deliverable, so they are exempt.
    if not is_router:
        if "references/provenance.md" not in linked:
            rep.error(name, "must link references/provenance.md (every sourced claim needs a locator)")
        for block in ("Evidence Ledger", "Handoff"):
            if block not in body:
                rep.error(name, f"output format must include a '{block}' block (see docs/conventions.md)")


def validate_symlinks(rep: Report) -> None:
    """Check the published `skills/` tree, which symlinks into the box directory.

    This is the tree a plugin loader actually walks, so the invocable name comes
    from the symlink, not from the directory it points at. A loader that requires
    frontmatter `name` to match the containing directory sees a mismatch here even
    though the box directory itself is internally consistent.
    """
    if not LINK_DIR.is_dir():
        return
    for entry in sorted(LINK_DIR.iterdir()):
        if entry.name == ".DS_Store":
            continue
        target = entry.resolve()
        if not target.is_dir():
            rep.error(f"skills/{entry.name}", "symlink does not resolve to a directory")
            continue
        skill_md = target / "SKILL.md"
        if not skill_md.is_file():
            rep.error(f"skills/{entry.name}", "target has no SKILL.md")
            continue
        fm, _ = split_frontmatter(skill_md.read_text(encoding="utf-8"))
        if fm is None:
            continue  # already reported against the box copy
        declared = parse_frontmatter(fm)[0].get("name", "")
        if declared and declared != entry.name:
            rep.warn(
                f"skills/{entry.name}",
                f"invoked as '{entry.name}' but frontmatter declares name {declared!r}",
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    args = parser.parse_args()

    rep = Report()
    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    for skill_dir in skill_dirs:
        validate_skill(skill_dir, rep)
    validate_symlinks(rep)

    if rep.errors:
        print(f"ERRORS ({len(rep.errors)})")
        for line in rep.errors:
            print(f"  ✗ {line}")
    if rep.warns:
        print(f"\nWARNINGS ({len(rep.warns)})")
        for line in rep.warns:
            print(f"  ! {line}")

    checked = f"\nChecked {len(skill_dirs)} skills"
    if not rep.errors and not rep.warns:
        print(f"{checked} — clean.")
        return 0
    print(f"{checked} — {len(rep.errors)} error(s), {len(rep.warns)} warning(s).")

    return 1 if rep.errors or (args.strict and rep.warns) else 0


if __name__ == "__main__":
    sys.exit(main())
