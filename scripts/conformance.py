#!/usr/bin/env python3
"""Score generated skill outputs against each skill's Deliverable Quality Bar.

Two layers, split along the line TypeSafe's own guidance draws: anything that is a
rule, a count, or an exact lookup stays in code; only genuine semantic judgment
goes to the model.

  structural  pure code -- does every item in section B also appear in table A,
              are there at least N of a thing, is a required section present.
  semantic    Jev Nouls -- is this value concrete rather than a placeholder, is
              this recommendation specific enough to write a ticket from.

Jev cannot count (documented jagged edge), so no question ever asks it to. Items
are enumerated in code and passed as a JSON array in `state`; one Noul per item
references `items[i]`, all in a single request, and the tally happens in code.

    python3 scripts/conformance.py --skills value-dams-and-flows --dry-run
    python3 scripts/conformance.py --skills value-dams-and-flows
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from box import EVAL_DIR, REPO, SKILLS_DIR, evals_path, short  # noqa: E402,F401
CACHE_DIR = EVAL_DIR / "generations"
TYPESAFE_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"


# --------------------------------------------------------------------- parsing

def strip_md(text: str) -> str:
    """Remove inline markdown so comparisons see the words, not the formatting."""
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"[*_`]+", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(set(c.strip()) <= set("-: ") and c.strip() for c in cells)


@dataclass
class Table:
    heading: str
    header: list[str]
    rows: list[list[str]]
    ancestry: list[str] = field(default_factory=list)

    def under(self, pattern: str, nearest: bool = False) -> bool:
        """Is this table anywhere beneath a heading matching `pattern`?

        Generated output often splits one logical section across subheadings --
        a Consequence Map with a table per feature -- so matching only the
        immediately preceding heading silently finds nothing.
        """
        # `nearest` for sibling tables under one parent: "Step 3 -- Values & Affected
        # Populations" holds both a values table and a populations table, and
        # matching the parent pulls each into the other's count.
        if nearest:
            return bool(re.search(pattern, self.heading, re.I))
        return any(re.search(pattern, h, re.I) for h in [*self.ancestry, self.heading])

    def column(self, name_fragment: str | list[str]) -> int | None:
        # A list is tried in order: the same column is "Evidence type" in one run
        # and plain "Type" in the next.
        for fragment in [name_fragment] if isinstance(name_fragment, str) else name_fragment:
            for i, h in enumerate(self.header):
                if fragment.lower() in h.lower():
                    return i
        return None


def parse_tables(text: str) -> list[Table]:
    """Every markdown table in the document, tagged with the heading above it."""
    tables: list[Table] = []
    stack: list[tuple[int, str]] = []
    pending: list[list[str]] = []

    def flush() -> None:
        nonlocal pending
        # header + separator + >=1 data row
        if len(pending) >= 2:
            header = pending[0]
            body = [r for r in pending[1:] if not is_separator(r)]
            if body:
                heading = stack[-1][1] if stack else ""
                ancestry = [h for _, h in stack[:-1]]
                tables.append(Table(heading, header, body, ancestry))
        pending = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [strip_md(c) for c in stripped.strip("|").split("|")]
            pending.append(cells)
            continue
        flush()
        if m := re.match(r"^(#{1,6})\s+(.*)$", stripped):
            level, title = len(m.group(1)), strip_md(m.group(2))
        elif m := re.match(r"^\*\*(.+?)\*\*:?\s*$", stripped):
            # Bold-label pseudo-heading. Without this, a table under **Anti-Hero
            # hits** had no section at all and no in_section pattern could reach it.
            level, title = 7, strip_md(m.group(1))
        else:
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, title))
    flush()
    return tables


def parse_headings(text: str) -> list[tuple[int, str]]:
    """(level, text) for real headings, ignoring fenced code blocks."""
    out: list[tuple[int, str]] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if m := re.match(r"^(#{1,6})\s+(.*)$", line):
            out.append((len(m.group(1)), strip_md(m.group(2))))
    return out


def _dividers(text: str) -> list[tuple[int, int, str]]:
    """(line index, level, title) for headings and bold-line pseudo-headings.

    Generated output frequently labels a section with a bold line rather than a
    real heading -- `**Section 9 - BOTTOM LINE**`, `**Future Direction**`. Treating
    only `#` as structure makes those sections invisible, which silently skips the
    criteria that depend on them.
    """
    out: list[tuple[int, int, str]] = []
    for i, line in enumerate(text.splitlines()):
        stripped = line.strip()
        if m := re.match(r"^(#{1,6})\s+(.*)$", stripped):
            out.append((i, len(m.group(1)), strip_md(m.group(2))))
        elif m := re.match(r"^\*\*(.+?)\*\*:?\s*$", stripped):
            # Weaker than any real heading, so a following `#` still closes it.
            out.append((i, 7, strip_md(m.group(1))))
        elif m := re.match(r"^\*\*([^*]{3,}?):\s*$", stripped):
            # A label whose bold was never closed ("**D. Five things ...:"). The
            # rubric judges content, not markdown hygiene.
            out.append((i, 7, strip_md(m.group(1))))
    return out


def section_texts(text: str, heading_pattern: str) -> list[str]:
    """Every section whose heading matches, each to its next same-or-higher heading."""
    lines = text.splitlines()
    dividers = _dividers(text)
    bodies = []
    for n, (idx, level, title) in enumerate(dividers):
        if not re.search(heading_pattern, title, re.I):
            continue
        end = next((i for i, lv, _ in dividers[n + 1:] if lv <= level), len(lines))
        bodies.append("\n".join(lines[idx:end]))
    return bodies


def section_text(text: str, heading_pattern: str, pick: str = "first") -> str:
    """Body under a heading matching the pattern, to the next same-or-higher one.

    `pick="last"` selects the final match, for bars about how a document *closes*.
    With an alternation pattern the first match is whichever alternative appears
    earliest, which is not the same thing.
    """
    lines = text.splitlines()
    dividers = _dividers(text)
    matches = [n for n, (_, _, title) in enumerate(dividers)
               if re.search(heading_pattern, title, re.I)]
    if not matches:
        return ""
    n = matches[-1] if pick == "last" else matches[0]
    idx, level, _ = dividers[n]
    for next_idx, next_level, _ in dividers[n + 1:]:
        if next_level <= level:
            return "\n".join(lines[idx:next_idx])
    return "\n".join(lines[idx:])


# ----------------------------------------------------------------- enumerators

def enumerate_items(text: str, spec: dict) -> list[str]:
    kind = spec["type"]

    if kind == "headings":
        # Includes bold-label pseudo-headings: the same skill labels a trade-off
        # entry "### Hard Dam: X" in one run and "**X (Hard Dam):**" in the next,
        # and reading only `#` headings made the second form enumerate nothing.
        pattern = spec["pattern"]
        return [
            title for _, _, title in _dividers(text)
            if re.search(pattern, title, re.I)
        ]

    if kind == "table_rows":
        rows = []
        for table in parse_tables(text):
            if not table.under(spec["in_section"], spec.get("nearest", False)):
                continue
            col = table.column(spec.get("column", "")) or 0
            for row in table.rows:
                if col >= len(row):
                    continue
                if flt := spec.get("where"):
                    idx = table.column(flt["column"])
                    if idx is None or idx >= len(row):
                        continue
                    if not re.search(flt["matches"], row[idx], re.I):
                        continue
                if row[col]:
                    rows.append(row[col])
        return rows

    if kind == "table_cells":
        cells = []
        for table in parse_tables(text):
            if not table.under(spec["in_section"], spec.get("nearest", False)):
                continue
            col = table.column(spec["column"])
            if col is None:
                continue
            # `skip_first`: a template's opening row can be a fixed bookend (a
            # backcast's end-state row) that the criterion does not cover.
            for row in table.rows[1 if spec.get("skip_first") else 0:]:
                if col >= len(row) or not row[col]:
                    continue
                # A criterion can legitimately apply to only some rows -- Conflict
                # Intensity is required for Dams and blank for Flows -- so filter
                # before asking, rather than manufacturing failures on rows the
                # quality bar never covered.
                if flt := spec.get("where"):
                    idx = table.column(flt["column"])
                    if idx is None or idx >= len(row):
                        continue
                    if not re.search(flt["matches"], row[idx], re.I):
                        continue
                cell = row[col]
                # `with_columns`: judge a cell beside others in its row -- a signal
                # is attributed by its Source cell, not by its own wording.
                for extra in spec.get("with_columns", []):
                    j = table.column(extra)
                    label = table.header[j] if j is not None else extra
                    value = row[j] if j is not None and j < len(row) and row[j] else "(none)"
                    cell += f"\n{label}: {value}"
                cells.append(cell)
        return cells

    if kind == "union":
        # The same artifact appears as bullets in one run and as table columns in
        # the next; enumerate every layout the skill produces and concatenate.
        return [item for part in spec["of"] for item in enumerate_items(text, part)]

    if kind == "phrase_matches":
        # Items identified by a fixed phrase the skill's template mandates
        # ("This design assumes ..."), whatever the surrounding format -- bullets,
        # bold paragraphs or a table all count.
        body = section_text(text, spec["in_section"]) if spec.get("in_section") else text
        return [strip_md(m.group(0)) for m in re.finditer(spec["pattern"], body, re.I)]

    if kind == "list_items":
        # Top-level bullets or numbered items in a section. Indented sub-bullets
        # are details of their parent, so counting them would inflate "at least 5".
        if spec.get("all_sections"):
            # A template can repeat a section per part (Four Futures has a D and an
            # E list for each future); collect the items from every match.
            one = {k: v for k, v in spec.items() if k != "all_sections"}
            return [item for body in section_texts(text, spec["in_section"])
                    for item in enumerate_items(body, one)]
        body = section_text(text, spec["in_section"])
        if spec.get("with_body"):
            # Keep each item's indented continuation ("   *Recommendation:* ..."):
            # a criterion about what an item says needs more than its first line.
            found = [strip_md(m.group(0)) for m in
                     re.finditer(r"^(?:[-*]|\d+[.)])\s+.+(?:\n(?:[ \t]+\S.*|[ \t]*$))*", body, re.M)]
            if found:
                return found
        found = [strip_md(m.group(1)) for m in
                 re.finditer(r"^(?:[-*]|\d+[.)])\s+(.+)$", body, re.M)]
        if not found:
            # Fall back to bold-led paragraphs: "**Voice-first booking** -- ..." or a
            # wholly bold title line, "**1. Human-touch fallback (Systemic)**".
            found = [strip_md(m.group(1)) for m in
                     re.finditer(r"^\*\*([^*\n]{3,}?)\*\*", body, re.M)]
            if spec.get("with_body"):
                # Bold-led items are pseudo-headings; their body is the section under them.
                found = [section_text(text, re.escape(f)) or f for f in found]
        if not found:
            # Last resort: items written as sub-headings ("### 1. Digital Accelerator").
            subs = [title for _, level, title in _dividers(body)[1:] if level < 7]
            found = [section_text(body, re.escape(s)) if spec.get("with_body") else s for s in subs]
        return found

    if kind == "list_after":
        # Bullets that follow an inline label ("**Robust design decisions:** These
        # hold in all four futures." then a list). The label is not a heading, so
        # section lookups cannot find it; stop at the first line that is neither
        # a bullet, an indented continuation nor blank.
        m = re.search(spec["label"], text, re.I)
        if not m:
            return []
        rest = text[text.find("\n", m.end()) + 1:] if "\n" in text[m.end():] else ""
        found: list[str] = []
        for line in rest.splitlines():
            if re.match(r"^(?:[-*]|\d+[.)])\s+", line):
                found.append(strip_md(re.sub(r"^(?:[-*]|\d+[.)])\s+", "", line)))
            elif line.strip() and not line.startswith((" ", "\t")):
                if found:
                    break
        return found

    raise ValueError(f"unknown enumerator type {kind!r}")


def norm(s: str) -> str:
    """Aggressive normalization for fuzzy containment between prose and table cells."""
    s = strip_md(s).lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s.replace("‑", "-").replace("–", "-"))
    return re.sub(r"\s+", " ", s).strip()


def count_parts(cell: str) -> int:
    """How many things does a cell list? "a; b; c", "1. a 2. b", "a, b (x, y)" -> 3, 2, 2.

    Parenthesised asides are dropped first so "(tiny checkboxes, low contrast)"
    does not count as two more entries, and so are qualifiers that open with
    "especially" or "e.g." -- they narrow the previous entry rather than add one.
    """
    text = re.sub(r"\([^()]*\)", "", strip_md(re.sub(r"<br\s*/?>", "; ", cell)))
    # Split on the strongest delimiter present: entries in a numbered or
    # semicolon list carry commas of their own inside the description.
    for delim in (r"(?:^|\s)\d+[.)]\s", r";|•", r","):
        if re.search(delim, text):
            break
    parts = re.split(delim, text)
    parts = [p.strip(" .") for p in parts]
    return sum(1 for p in parts
               if len(p) > 2 and not re.match(r"(especially|including|e\.g|such as|i\.e)\b", p, re.I))


def overlaps(needle: str, haystack: list[str]) -> bool:
    """Does `needle` correspond to any entry in `haystack`?

    Generated prose renames things between sections ("Everything Free" in a heading
    vs "Keep everything free forever" in a table), so exact matching would produce
    false failures. Compares significant-word overlap instead.
    """
    STOP = {"the", "a", "an", "of", "for", "and", "or", "to", "in", "all", "no", "with"}
    n_words = {w for w in norm(needle).split() if w not in STOP and len(w) > 2}
    if not n_words:
        return False
    for candidate in haystack:
        c_words = {w for w in norm(candidate).split() if w not in STOP and len(w) > 2}
        if not c_words:
            continue
        shared = n_words & c_words
        if len(shared) / min(len(n_words), len(c_words)) >= 0.5:
            return True
    return False


# --------------------------------------------------------------- Jev transport

def ask_jev(state, questions: dict, api_key: str, attempts: int = 5) -> dict:
    """POST one System One request, retrying transient failures.

    TypeSafe's API docs ask clients to back off and retry on 429 and 529. Without
    this, one overloaded response aborted a whole scoring run and wrote nothing.
    """
    import http.client
    import random
    import time

    body = json.dumps({"state": state, "model": MODEL, "questions": questions}).encode()
    last = ""
    for attempt in range(attempts):
        request = urllib.request.Request(
            TYPESAFE_ENDPOINT, data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=300) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as exc:
            last = f"Jev {exc.code}: {exc.read().decode()[:300]}"
            if exc.code not in (408, 429, 500, 502, 503, 504, 529):
                raise RuntimeError(last) from exc
        except (urllib.error.URLError, TimeoutError, http.client.HTTPException,
                ConnectionError, json.JSONDecodeError) as exc:
            last = f"{type(exc).__name__}: {exc}"
        if attempt < attempts - 1:
            time.sleep(min(30, 2 ** attempt) + random.uniform(0, 1))
    raise RuntimeError(f"Jev request failed after {attempts} attempts: {last}")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for line in (EVAL_DIR / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def lookup_prompt(skill: str, scenario: str) -> str:
    """The originating prompt, needed by bars that depend on what was asked for.

    Generations do not store it, so recover it from the eval set by scenario name,
    falling back to the id-derived name the harness uses when `name` is absent.
    """
    path = evals_path(skill)
    if not path.is_file():
        return ""
    for entry in json.loads(path.read_text())["evals"]:
        if (entry.get("name") or f"eval-{entry.get('id')}") == scenario:
            return entry["prompt"]
    return ""


# ------------------------------------------------------------------- scoring

# Jev returns a probability; code owns the thresholds. Anything between the two
# goes to a person rather than either bucket -- the three-way split TypeSafe's
# Confidence page recommends. These are provisional until calibration.
YES, NO = 0.70, 0.30


def score_document(doc: str, spec: dict, api_key: str | None, prompt: str = "") -> dict:
    items = {name: enumerate_items(doc, e) for name, e in spec["enumerators"].items()}
    result = {"enumerated": {k: len(v) for k, v in items.items()},
              "structural": [], "semantic": []}

    for check in spec["structural"]:
        kind = check["kind"]
        if kind == "subset":
            source = items[check["items"]]
            missing = [i for i in source if not overlaps(i, items[check["within"]])]
            if not source:
                # "every element of the empty set is in the map" is vacuously true.
                # A document that produced no items at all did not satisfy the bar,
                # so record it as a failure rather than a free pass.
                passed, detail = False, {"vacuous": True}
            else:
                passed, detail = not missing, {"missing": missing}
                if missing and check.get("or_count"):
                    # Later sections often rename items by instance ("Buried
                    # opt-out") instead of type ("Roach Motel"); one row per item
                    # is also coverage, even when no name carries across.
                    passed = len(items[check["within"]]) >= len(source)
        elif kind == "min_count":
            got = len(items[check["items"]])
            hi = check.get("max", 10**9)
            passed = check["n"] <= got <= hi
            need = check["n"] if hi == 10**9 else f"{check['n']}-{hi}"
            detail = {"found": got, "required": need}
        elif kind == "section_present":
            passed = bool(section_text(doc, check["pattern"]))
            detail = {}
        elif kind == "distinct_coverage":
            # "spans at least 4 of the 6 harm categories" -- set arithmetic, not a
            # judgment, and Jev explicitly cannot count.
            blob = " ".join(items[check["items"]]).lower()
            found = sorted(v for v in check["vocabulary"] if v.lower() in blob)
            passed = len(found) >= check["n"]
            detail = {"found": len(found), "required": check["n"], "covered": found}
        elif kind == "vocabulary_range":
            # "uses 2-5 cards": distinct deck terms mentioned anywhere in the doc.
            text_n = re.sub(r"[\u2010-\u2015]", "-", doc).lower()
            found = sorted(v for v in check["vocabulary"] if v.lower() in text_n)
            lo, hi = check.get("min", 0), check.get("max", 10**9)
            passed = lo <= len(found) <= hi
            detail = {"found": len(found), "required": f"{lo}-{hi}", "covered": found}
        elif kind == "cells_in_vocabulary":
            # Every card a table names must be a real card from the deck -- an
            # invented "Deceiver" breaks the shared vocabulary the method exists for.
            vocab = [v.lower() for v in check["vocabulary"]]
            cells = items[check["items"]]
            norm_c = lambda c: re.sub(r"[\u2010-\u2015]", "-", c).lower()
            bad = [c for c in cells if not any(v in norm_c(c) for v in vocab)]
            passed = bool(cells) and not bad
            detail = {"failing_cells": bad, "vacuous": not cells}
        elif kind == "pairs_present":
            # For every left-hand term used, one of its paired right-hand terms must
            # also appear: an Anti-Hero named without its Hero counter-move is a
            # critique with no way out.
            text_n = re.sub(r"[\u2010-\u2015]", "-", doc).lower()
            # A card merely considered and rejected in prose is not a card used.
            # Prefer the cards the output actually tabulates, when it has tables.
            source = " ".join(items.get(check.get("used_in", ""), [])).lower()
            source = re.sub(r"[\u2010-\u2015]", "-", source) or text_n
            used = [a for a in check["pairs"] if a.lower() in source]
            missing = [a for a in used
                       if not any(h.lower() in text_n for h in check["pairs"][a])]
            passed = bool(used) and not missing
            detail = {"missing": [f"{a} (no {' / '.join(check['pairs'][a])})" for a in missing],
                      "vacuous": not used}
        elif kind == "captures_differ":
            # "runs a second cycle on a different assumption than the first":
            # compare the two stated assumptions by significant-word overlap.
            # Each capture is searched inside its own section when one is given: the
            # label wording varies run to run ("Assumption in focus / selected /
            # picked"), and a doc-wide search lets one pattern hit the other cycle.
            def capture(patterns, section):
                # Try patterns in order: the label, the mandated phrase, a quoted
                # assumption in prose, a heading parenthetical. Returns the first hit.
                body = section_text(doc, section) if section else doc
                for pat in patterns if isinstance(patterns, list) else [patterns]:
                    if m := re.search(pat, body, re.I | re.M):
                        return m
                return None
            a = capture(check["first"], check.get("first_section"))
            b = capture(check["second"], check.get("second_section"))
            if not a or not b:
                passed, detail = False, {"vacuous": True}
            else:
                wa, wb = (set(norm(x.group(1)).split()) - {"the", "user", "this", "design",
                          "assumes", "that", "can", "has", "and", "a", "to", "of"} for x in (a, b))
                overlap = len(wa & wb) / max(1, min(len(wa), len(wb)))
                passed = overlap < check.get("max_overlap", 0.6)
                detail = {"overlap": round(overlap, 2)}
        elif kind == "per_key_min":
            # "at least 2 populations per move": join a detail table back to the
            # inventory by the number in each key ("1", "M1", "Move 1" all -> 1).
            def key(cell):
                m = re.search(r"\d+", cell)
                return m.group(0) if m else cell.strip().lower()
            keys = [key(k) for k in items[check["keys"]]]
            counts: dict[str, int] = {}
            for cell in items[check["rows"]]:
                # One detail row may cover several moves: "1, 3" or "M2/M4".
                for k in (re.findall(r"\d+", cell) or [cell.strip().lower()]):
                    counts[k] = counts.get(k, 0) + 1
            short = [k for k in keys if counts.get(k, 0) < check["n"]]
            passed = bool(keys) and not short
            detail = {"found": len(keys) - len(short), "required": len(keys),
                      "missing": [f"move {k}: {counts.get(k, 0)} of {check['n']}" for k in short]}
        elif kind == "group_parts_min":
            # "at least 3 named populations per pattern": outputs list them three
            # ways -- "a; b; c" in one cell, "1. a 2. b 3. c", or one row each with
            # the pattern cell repeated or left blank. Group rows by the key column
            # (blank = continuation of the row above) and count listed parts.
            groups: dict[str, int] = {}
            named = items[check["group_by"]] if check.get("group_by") else []
            for table in parse_tables(doc):
                if not table.under(check["in_section"], check.get("nearest", False)):
                    continue
                kc, vc = table.column(check["key"]), table.column(check["value"])
                if kc is None or vc is None:
                    continue
                current = ""
                for row in table.rows:
                    if max(kc, vc) >= len(row):
                        continue
                    current = norm(strip_md(row[kc])) or current
                    # A row keyed "Roach Motel / Misdirection" counts toward both
                    # audited patterns; one keyed by an instance name stands alone.
                    targets = [k for k in named if overlaps(k, [current])] or [current]
                    for t in targets:
                        groups[t] = groups.get(t, 0) + count_parts(row[vc])
            short = [f"{k[:40]}: {v}" for k, v in groups.items() if v < check["n"]]
            passed = bool(groups) and not short
            detail = {"missing": short, "vacuous": not groups}
        elif kind == "not_copied":
            # "specific to the product audited, not generic": an item lifted from
            # the skill's own examples is by construction not product-specific.
            def words(s):
                return {w for w in norm(s).split() if len(w) > 2}
            copied = []
            for item in items[check["items"]]:
                iw = words(item)
                for ex in check["examples"]:
                    ew = words(ex)
                    if iw and len(iw & ew) / len(ew) >= check.get("threshold", 0.7):
                        copied.append(item[:80])
                        break
            passed = bool(items[check["items"]]) and not copied
            detail = {"copied": copied, "vacuous": not items[check["items"]]}
        elif kind == "all_phrases":
            body = section_text(doc, check["section"])
            absent = [ph for ph in check["phrases"] if not re.search(ph, body, re.I)]
            passed = bool(body) and not absent
            detail = {"missing": absent, "vacuous": not body}
        elif kind == "count_covers":
            # "maps each pledge": the traced rows must cover every pledge listed,
            # not merely reach a fixed floor.
            got, need = len(items[check["items"]]), len(items[check["covers"]])
            passed = need > 0 and got >= need
            detail = {"found": got, "required": need, "vacuous": need == 0}
        elif kind == "min_count_matching":
            matching = [c for c in items[check["items"]] if re.search(check["pattern"], c, re.I)]
            passed = len(matching) >= check["n"]
            detail = {"found": len(matching), "required": check["n"]}
        elif kind == "conditional_section":
            # Some bars depend on what was actually asked for -- dah-cards must not
            # emit a Manifesto unless the user requested one. Needs the prompt.
            requested = bool(re.search(check["when_prompt_matches"], prompt, re.I))
            present = bool(section_text(doc, check["pattern"]))
            # `required_only`: the section is owed when triggered, harmless otherwise.
            passed = (present or not requested) if check.get("required_only") else (present == requested)
            detail = {"requested": requested, "present": present}
        elif kind == "any_of":
            # "completes all five tools OR states which were run and why" -- the
            # bar is genuinely disjunctive, so flattening it would fail correct work.
            outcomes = []
            for sub in check["checks"]:
                if sub["kind"] == "min_count":
                    outcomes.append(len(items[sub["items"]]) >= sub["n"])
                elif sub["kind"] == "section_present":
                    outcomes.append(bool(re.search(sub["pattern"], doc, re.I)))
                else:
                    raise ValueError(f"any_of cannot nest {sub['kind']!r}")
            passed = any(outcomes)
            detail = {"branches": outcomes}
        elif kind == "section_implies_section":
            # A tool that did not run cannot owe its output. Only require the
            # consequent when the antecedent is actually present.
            # Match a real section, not a passing mention: a run that consumed a
            # *prior* Ethics Frame as input does not owe an Ethics Frame's output.
            antecedent = bool(section_text(doc, check["if_present"]))
            consequent = bool(re.search(check["then_present"], doc, re.I))
            passed = consequent or not antecedent
            detail = {"antecedent": antecedent, "consequent": consequent}
        elif kind == "implied_section":
            # If the trigger set is non-empty, the section becomes required.
            triggered = bool(items[check["items"]])
            present = bool(re.search(check["pattern"], doc, re.I))
            passed = present or not triggered
            detail = {"triggered_by": len(items[check["items"]]), "present": present}
        elif kind == "descending_years":
            # "builds the timeline backwards": the first year in each row, read top
            # to bottom, never increases. A forward roadmap printed in reverse
            # passes this too, which is why the semantic layer also asks.
            years = [int(m.group(0)) for c in items[check["items"]]
                     if (m := re.search(r"\b(?:19|20)\d\d\b", c))]
            rising = [f"{a} -> {b}" for a, b in zip(years, years[1:]) if b > a]
            passed = len(years) >= check.get("min", 3) and not rising
            detail = {"years": years, "rising": rising, "vacuous": not years}
        elif kind == "no_new_numbers":
            # "adds no figures to user-supplied signals": every number in these
            # items must already be in the user's brief. Exact lookup, so code.
            brief = set(re.findall(r"\d+(?:[.,]\d+)?", prompt))
            added = [f"{n} in: {c[:60]}" for c in items[check["items"]]
                     for n in re.findall(r"\d+(?:[.,]\d+)?", c) if n not in brief]
            passed = not added
            detail = {"missing": added, "vacuous": not items[check["items"]]}
        elif kind == "distinct_cells":
            # "a different problem-solver at different layers", "weights differ
            # between images": count distinct values after normalising.
            cells = items[check["items"]]
            distinct = {norm(c) for c in cells if norm(c)}
            passed = len(distinct) >= check["n"]
            detail = {"found": len(distinct), "required": check["n"], "vacuous": not cells}
        elif kind == "pattern_absent":
            # "calls no future best, worst or most likely". A line that states the
            # rule ("no future is ranked most likely") is not a breach of it.
            negated = re.compile(r"\b(?:no|not|never|none|neither|nor|without|avoid\w*|isn't|aren't|don't|do not)\b", re.I)
            hits = [m.group(0).strip()[:90] for m in re.finditer(r"[^\n]*(?:" + check["pattern"] + r")[^\n]*", doc, re.I)
                    if not negated.search(m.group(0))]
            passed = not hits
            detail = {"missing": [f"breach: {h}" for h in hits]}
        elif kind == "cells_match":
            # A criterion a regex can decide belongs here, not in the semantic
            # layer. Jev reads literally and is explicitly not a calculator, so
            # asking it "is there a number 1-5 in this cell" both wastes a call
            # and introduces avoidable variance.
            cells = items[check["items"]]
            bad = [c for c in cells if not re.search(check["pattern"], c)]
            passed = bool(cells) and not bad
            detail = {"failing_cells": bad, "vacuous": not cells}
        else:
            raise ValueError(f"unknown structural check {kind!r}")
        entry = {"id": check["id"], "passed": passed, "desc": check["desc"], **detail}
        if check.get("allow_vacuous") and detail.get("vacuous"):
            # Some modes legitimately produce none of the items a check inspects
            # (ethical-dialogue mode has no card tables). Record as not applicable.
            entry["not_applicable"] = True
        result["structural"].append(entry)

    # Build one Jev request per criterion: state is the array of enumerated items,
    # one question per item. Jev ingests state once and answers in parallel.
    for check in spec["semantic"]:
        if check.get("scope") == "tail":
            # For bars about how a document *closes*: the final quarter, at least
            # 15 lines. Independent of what the closing section happens to be
            # called, so an edit that renames it cannot move the score by itself.
            lines = doc.splitlines()
            values = ["\n".join(lines[-max(15, len(lines) // 4):])]
        elif check.get("scope") == "document":
            # Bars about the whole chain ("at least 5 values across the chain")
            # need the whole document, not whichever heading matched first.
            values = [doc]
        elif "section" in check:
            # A whole-document judgment rather than a per-item one. Scope the state
            # to the relevant section: accuracy falls as state grows with detail
            # unrelated to the question.
            body = section_text(doc, check["section"], check.get("pick", "first"))
            values = [body] if body.strip() else []
        else:
            values = items[check["each"]]
            if check.get("scope_section"):
                # For heading-based items, send the section body, not the title.
                values = [section_text(doc, re.escape(v)) or v for v in values]

        entry = {"id": check["id"], "bar": check["bar"], "n": len(values)}
        if not values:
            entry |= {"skipped": "no items enumerated", "results": []}
            result["semantic"].append(entry)
            continue
        if api_key is None:
            entry |= {"skipped": "dry-run", "results": []}
            result["semantic"].append(entry)
            continue

        kind = check.get("type", "noul")
        questions = {
            f"item_{i}": {
                "type": kind,
                "instructions": check["instructions"].replace("{i}", str(i)),
                "criteria": check["criteria"],
            }
            for i in range(len(values))
        }
        state = {"items": values}
        if check.get("with_prompt"):
            # Bars that compare output with input ("adds nothing to the user's
            # signals") need the brief. As its own state field, not pasted into each
            # item: calibration found Jev cannot compare two texts packed into one
            # string (every case scored ~0.35), but separates them as two fields.
            state["brief"] = prompt
        if check.get("one_per_request"):
            # Some criteria shift with their neighbours in a batch (calibration found
            # a named bank scoring 0.23 among five items and 0.87 alone); send each
            # item alone, as calibrate.py does for them.
            q0 = {"item_0": questions["item_0"]}
            singles = [ask_jev(state | {"items": [v]}, q0, api_key) for v in values]
            answers = [r["answers"]["item_0"] for r in singles]
            response = {"usage": {"input_tokens": sum(r["usage"]["input_tokens"] for r in singles)}}
        else:
            response = ask_jev(state, questions, api_key)
            answers = [response["answers"][f"item_{i}"] for i in range(len(values))]

        if kind == "score":
            # Jev cannot reconstruct an exact number by interpolating between
            # levels, but thresholding the expectation against a named level is
            # supported. `min_level` is the index the answer must reach.
            floor = check["min_level"]
            scores = [a["score"] for a in answers]
            verdicts = ["pass" if s >= floor else "fail" for s in scores]
            entry |= {
                "results": [
                    {"item": v[:90], "noul": round(s, 2), "verdict": verdict,
                     "legend": a.get("legend", {}).get(str(int(round(s))), "")}
                    for v, s, verdict, a in zip(values, scores, verdicts, answers)
                ],
                "passed": all(v == "pass" for v in verdicts),
                "min_level": floor,
            }
        else:
            scores = [a["noul"] for a in answers]
            entry |= {
                "results": [
                    {"item": v[:90], "noul": round(s, 3),
                     "verdict": "pass" if s >= YES else "fail" if s < NO else "review"}
                    for v, s in zip(values, scores)
                ],
                # `min_pass`: "at least two concrete pockets" -- Jev judges each item,
                # code counts, because Jev cannot count.
                "passed": (sum(s >= YES for s in scores) >= check["min_pass"]) if check.get("min_pass")
                          else all(s >= YES for s in scores),
                "needs_review": [round(s, 3) for s in scores if NO <= s < YES],
            }
        entry["input_tokens"] = response["usage"]["input_tokens"]
        result["semantic"].append(entry)

    return result


def select_generations(
    wanted: list[str] | None, arm: str, reps: int, skill_ref: str | None = None,
    web_search: int = 0,
) -> tuple[list, list[str]]:
    """Generations matching the *current* SKILL.md, via the harness's own task keys.

    The cache keeps every version a skill has ever had. Scoring by glob would mix
    outputs from before and after an edit and report their average as either one.
    Returns (matched, missing labels).
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from run_generation import DEFAULT_MODEL, build_tasks  # noqa: E402

    arms = ("without_skill", "with_skill") if arm == "both" else (arm,)
    tasks = build_tasks(wanted, None, DEFAULT_MODEL, reps, arms, skill_ref, web_search)
    matched, missing = [], []
    for task in tasks:
        spec_path = SKILLS_DIR / task.skill / "conformance.json"
        if not spec_path.is_file():
            continue
        gen_path = CACHE_DIR / f"{task.key}.json"
        if not gen_path.is_file():
            missing.append(task.label)
            continue
        d = json.loads(gen_path.read_text())
        d["prompt"] = task.prompt
        d["rep"] = task.rep
        matched.append((d, json.loads(spec_path.read_text())))
    return matched, missing


def print_document(doc: dict, scored: dict) -> None:
    rep = f" #{doc['rep']}" if doc.get("rep") else ""
    print(f"\n{'='*78}\n{short(doc['skill'])} / {doc['scenario']}{rep} [{doc['arm']}]\n{'='*78}")
    print("  enumerated: " + ", ".join(f"{k}={v}" for k, v in scored["enumerated"].items()))
    print("\n  STRUCTURAL (code)")
    for c in scored["structural"]:
        mark = "n/a " if c.get("not_applicable") else "PASS" if c["passed"] else "FAIL"
        print(f"    [{mark}] {c['desc']}")
        if c.get("vacuous"):
            print("           vacuous: no items were produced to check")
        for m in c.get("missing", []):
            print(f"           not in map: {m[:70]}")
        for cell in c.get("failing_cells", []):
            print(f"           cell fails pattern: {cell[:60]!r}")
        if "found" in c and not c["passed"]:
            print(f"           found {c['found']}, need {c['required']}")
        if "covered" in c:
            print(f"           covered: {', '.join(c['covered']) or '(none)'}")
        if "requested" in c and not c["passed"]:
            print("           " + ("requested but absent" if c["requested"] else "present but never requested"))
        if "triggered_by" in c and not c["passed"]:
            print(f"           required by {c['triggered_by']} finding(s), but absent")
        if "antecedent" in c:
            state = "required and present" if c["antecedent"] and c["consequent"] else \
                    "required but absent" if c["antecedent"] else "not required"
            print(f"           {state}")
    print("\n  SEMANTIC (Jev)")
    for c in scored["semantic"]:
        if "skipped" in c:
            print(f"    [skip] {c['id']} ({c['skipped']}, {c['n']} items)")
            continue
        print(f"    [{'PASS' if c['passed'] else 'FAIL'}] {c['id']}  ({c['n']} items)")
        for r in c["results"]:
            print(f"           {r['noul']:.2f} {r['verdict']:6s} {r['item'][:62]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills", help="comma-separated skill names")
    parser.add_argument("--arm", default="with_skill", choices=["with_skill", "without_skill", "both"])
    parser.add_argument("--reps", type=int, default=1, help="score reps 0..N-1 per scenario")
    parser.add_argument("--skill-ref", help="score generations made from SKILL.md as of this git ref")
    parser.add_argument("--json", metavar="PATH", help="write per-check pass rates here")
    parser.add_argument("--quiet", action="store_true", help="summary only, no per-document detail")
    parser.add_argument("--web-search", type=int, default=0, metavar="N",
                        help="score the generations made with run_generation.py --web-search N")
    parser.add_argument("--dry-run", action="store_true", help="enumerate only, no Jev calls")
    args = parser.parse_args()

    wanted = [s.strip() for s in args.skills.split(",")] if args.skills else None
    api_key = None if args.dry_run else load_env().get("TYPESAFE_API_KEY")
    if not args.dry_run and not api_key:
        sys.exit("TYPESAFE_API_KEY not found in eval-framework/.env")

    generations, missing = select_generations(wanted, args.arm, args.reps, args.skill_ref,
                                              args.web_search)
    if missing:
        print(f"! {len(missing)} expected generation(s) not in cache -- run run_generation.py first:")
        for label in missing[:10]:
            print(f"    {label}")
    if not generations:
        sys.exit("no generations matched (need a conformance.json and cached output)")

    # check id -> outcome counts, per skill. A per-item semantic check passes for a
    # document only if every item passes; "skip" means nothing was enumerated.
    rates: dict[str, dict[str, dict[str, int]]] = {}
    documents: list[dict] = []

    for doc, spec in generations:
        scored = score_document(doc["output"], spec, api_key, doc.get("prompt", ""))
        if not args.quiet:
            print_document(doc, scored)
        skill_rates = rates.setdefault(doc["skill"], {})
        outcome_row = {"skill": doc["skill"], "scenario": doc["scenario"],
                       "rep": doc.get("rep", 0), "arm": doc["arm"], "checks": {}}
        for c in scored["structural"]:
            o = "skip" if c.get("not_applicable") else "pass" if c["passed"] else "fail"
            skill_rates.setdefault(c["id"], {"pass": 0, "fail": 0, "skip": 0, "review": 0})[o] += 1
            outcome_row["checks"][c["id"]] = o
        for c in scored["semantic"]:
            bucket = skill_rates.setdefault(c["id"], {"pass": 0, "fail": 0, "skip": 0, "review": 0})
            if "skipped" in c:
                o = "skip"
            elif c["passed"]:
                o = "pass"
            elif any(r["verdict"] == "review" for r in c["results"]) and \
                    not any(r["verdict"] == "fail" for r in c["results"]):
                o = "review"
            else:
                o = "fail"
            bucket[o] += 1
            outcome_row["checks"][c["id"]] = o
        documents.append(outcome_row)

    print(f"\n{'='*78}\nPER-CHECK PASS RATE  ({args.arm}, {args.reps} rep(s) per scenario)\n{'='*78}")
    grand_pass = grand_total = 0
    for skill, checks in rates.items():
        print(f"\n{short(skill)}")
        for cid, o in checks.items():
            scored_n = o["pass"] + o["fail"] + o["review"]
            grand_pass += o["pass"]
            grand_total += scored_n + o["skip"]
            extra = "".join(f", {o[k]} {k}" for k in ("review", "skip") if o[k])
            flag = "" if o["fail"] == 0 and o["skip"] == 0 else "  <--"
            print(f"  {cid:36s} {o['pass']:>2}/{scored_n + o['skip']:<2} pass{extra}{flag}")
    if grand_total:
        print(f"\noverall: {grand_pass}/{grand_total} check-document pairs pass "
              f"({100 * grand_pass / grand_total:.0f}%)")

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps({"arm": args.arm, "reps": args.reps,
                                               "rates": rates, "documents": documents}, indent=2))
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
