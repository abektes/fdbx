#!/usr/bin/env python3
"""Mechanical checks on baseline (without_skill) generations.

The baseline probe asks one question per skill: when a capable model is only told
the method's name, does it make the specific mistakes the skill was written to
prevent? CHECKS are regexes or counts, reliable only for surface features (is a
layer named, is a future called "most likely"). MANUAL_CHECKS are judgement calls
that a regex gets wrong in both directions; they are read per output and recorded
in docs/baseline-probe-batch-1.md. Read flagged outputs before believing any rate.

    python3 scripts/probe_baseline.py                 # all skills, without_skill arm
    python3 scripts/probe_baseline.py --arm with_skill
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass

from box import EVAL_DIR

CACHE_DIR = EVAL_DIR / "generations"
I = re.IGNORECASE


def has(pattern: str):
    rx = re.compile(pattern, I)
    return lambda text: bool(rx.search(text))


NEGATED = re.compile(r"\b(?:no|none|not|never|neither|nor|without|avoid\w*|isn't|aren't|don't|do not)\b", I)


def has_unnegated(pattern: str):
    """A hit only if some matching line is not a negation. Skills tell the model
    what *not* to do ("no future is labelled most likely"), and outputs often repeat
    that rule back; counting the echo as the failure would invert the result."""
    rx = re.compile(r"[^\n]*(?:" + pattern + r")[^\n]*", I)
    return lambda text: any(not NEGATED.search(m.group(0)) for m in rx.finditer(text))


def lacks(pattern: str):
    rx = re.compile(pattern, I)
    return lambda text: not rx.search(text)


def count_at_least(patterns: list[str], n: int):
    rxs = [re.compile(p, I) for p in patterns]
    return lambda text: sum(bool(rx.search(text)) for rx in rxs) >= n


@dataclass
class Check:
    id: str
    question: str
    failure_if_true: bool  # True: a hit is the failure the skill prevents
    fn: object


NUMERIC_CLAIM = r"\b\d{1,3}(?:\.\d+)?\s?%|\$\s?\d[\d,.]*\s?(?:bn|billion|m|million|k)?\b"

CHECKS: dict[str, list[Check]] = {
    "fdbx-four-futures": [
        Check("all_four_types", "names all four generic futures (growth, collapse, discipline, transformation)", False,
              count_at_least([r"continu\w* growth|continuation", r"collapse", r"discipline", r"transformation"], 4)),
        Check("ranks_a_future", "labels a future best / worst / most likely", True,
              has_unnegated(r"\bmost (?:likely|probable|plausible)\b|\blikeliest\b|\bbest[- ]case\b|\bworst[- ]case\b")),
        Check("steady_state_name", "uses 'steady state' (Inayatullah's alias) instead of Dator's 'discipline'", True,
              has(r"steady[- ]state")),
        Check("five_things", "gives 'five things to do now' per future (Dator's D/E questions)", False,
              has(r"five (?:things|actions|moves|steps)")),
        Check("artifact", "includes an artifact from the future (headline, notice, diary)", False,
              has(r"artifact|artefact|headline|diary entry|news clipping")),
    ],
    "fdbx-three-horizons": [
        Check("mckinsey_framing", "uses McKinsey growth framing (core/adjacent, Baghai, Alchemy of Growth)", True,
              has_unnegated(r"\bcore business\b|\badjacen\w+|mckinsey|baghai|alchemy of growth|\b70\s*/\s*20\s*/\s*10\b")),
        Check("horizons_as_time_bands", "defines horizons as successive time bands (0-1 yr, 1-3 yrs...)", True,
              has(r"H1[^\n]{0,60}\b(?:0|1)\s*[-–]\s*\d+\s*(?:years|yrs|months)|horizon 1[^\n]{0,60}\b(?:0|1)\s*[-–]\s*\d+\s*(?:years|yrs|months)")),
        Check("h2_plus_minus", "distinguishes H2+ from H2-", False,
              has(r"H2\s*(?:\+|plus|\(\+\))|H2\s*(?:-|−|minus|\(-\))")),
        Check("pockets", "names pockets of the future in the present", False,
              has(r"pockets? of (?:the )?future")),
        Check("mindsets", "uses manager / entrepreneur / visionary perspectives", False,
              count_at_least([r"manag(?:er|erial)", r"entrepreneur", r"visionar"], 3)),
    ],
    "fdbx-causal-layered-analysis": [
        Check("four_layers", "names all four layers (litany, social/systemic causes, worldview/discourse, myth/metaphor)", False,
              count_at_least([r"litany", r"social causes|systemic causes|systemic", r"worldview|discourse", r"myth|metaphor"], 4)),
        Check("reframes", "reframes the brief or problem (any wording)", False,
              has(r"refram\w*|reconstruct\w*|new litany|mov\w+ back up|rebuil\w*")),
        Check("alt_metaphor", "proposes an alternative / new metaphor", False,
              has(r"(?:alternative|new|different|replacement) (?:root )?(?:metaphor|myth|story)")),
        Check("scenarios", "writes scenarios", False, has(r"scenario")),
        Check("problem_solver", "names who acts / the problem-solver per layer", False,
              has(r"problem[- ]solver|who acts")),
    ],
    "fdbx-futures-triangle": [
        Check("archetypes", "names at least two of the distinctive archetypes (evolution and progress, Gaia, globalism, back to the future)", False,
              count_at_least([r"evolution and progress", r"\bgaia", r"globalism", r"back to the future"], 2)),
        Check("used_future", "asks whether the strategy serves a used or disowned future", False,
              has(r"used future|disowned future")),
        Check("weights_per_image", "gives weights per image", False,
              has(r"barriers? by image|weights? by image|weights? (?:per|for each) image")),
    ],
    # Batch 2 candidates. Probed before any SKILL.md was written, to decide which
    # methods a skill would add to (docs/baseline-probe-batch-2.md).
    "fdbx-futures-wheel": [
        # The plain model says "first-/second-/third-order" rather than Glenn's words.
        Check("three_rings", "names three rings of consequences (primary/secondary/tertiary or 1st-3rd order)", False,
              count_at_least([r"primary|first[- ]order", r"secondary|second[- ]order", r"tertiary|third[- ]order"], 3)),
        Check("domains_first", "sets impact domains (PESTLE/STEEP, Glenn's Version 2)", False,
              has(r"PESTLE|STEEP|PEST\b|domains? of (?:impact|consequence)|version 2")),
        Check("cross_links", "links consequences across branches", False,
              has(r"cross[- ]?link|cross[- ]?impact|interconnect|interact\w* (?:between|across) branch")),
        Check("feedback_loop", "names a consequence that cycles back (feedback loop)", False,
              has(r"feedback loop|loops? back|reinforcing loop|vicious (?:circle|cycle)|virtuous (?:circle|cycle)")),
        Check("contradiction", "keeps contradictory consequences side by side", False,
              has(r"contradict\w*|tension between|opposite (?:effects?|consequences?)")),
        Check("causality_caveat", "warns that the wheel shows plausible links, not causes or predictions", False,
              has(r"correlation|not (?:a )?predict\w*|not causal|speculative")),
    ],
    "fdbx-futures-cone": [
        Check("five_classes", "names projected, probable, plausible, possible and preposterous", False,
              count_at_least([r"projected", r"probable", r"plausible", r"\bpossible", r"preposterous"], 5)),
        Check("preferable_spans", "treats preferable as a judgement that can sit in any class", False,
              has(r"preferab\w+[^\n]{0,160}(?:any|across|anywhere|overlap|cut\w* across|span)|normative")),
        Check("judgement_in_present", "says the classes are judgements made now, which change over time", False,
              has(r"judge?ment|subjective|shift\w* (?:between|across) (?:classes|categories)|mov\w+ (?:from|between) (?:classes|categories|zones)")),
        Check("wildcards", "includes wildcards", False, has(r"wild ?cards?")),
        Check("potential_outside", "names 'potential' futures outside the cone", False, has(r"\bpotential futures?\b")),
        Check("predicted_class", "uses a 'predicted' class (Voros dropped it)", True, has(r"\bpredicted futures?\b")),
    ],
    "fdbx-backcasting": [
        Check("end_state", "states a preferred future / end state", False,
              has(r"preferred future|end[- ]state|desired future|vision (?:statement|of)")),
        Check("differences", "lists key differences between present and preferred future", False,
              has(r"key differences|gap (?:analysis|between)|today vs|present vs|from[^\n]{0,20}to[^\n]{0,20}(?:table|comparison)")),
        Check("control_scoring", "scores events wholly / partly / out of our control", False,
              has(r"(?:wholly|partly|partially|fully|outside|out of|beyond)[^\n]{0,15}(?:our |your )?control")),
        Check("winners_losers", "asks who benefits and who loses from each event", False,
              has(r"los(?:e|es|ers?) out|who (?:benefits|loses)|winners? and losers?")),
        Check("influence_outside", "plans influence over steps outside control", False,
              has(r"who has control|influenc\w+[^\n]{0,40}(?:outside|beyond|not in)")),
        Check("forward_vs_backward", "contrasts backcasting with forecasting / forward planning", False,
              has(r"forecast\w*|forward[- ]plann\w*|present bias")),
    ],
    "fdbx-design-fiction": [
        Check("artifact_rendered", "renders a concrete artifact from the future (the thing itself, not a description)", False,
              has(r"^>|```|\bnotice\b|\bletter\b|\bmanual\b|\breceipt\b|\badvert|\bpackaging\b|\bpolicy document\b|\bscreen\b")),
        Check("diegetic", "uses Kirby's diegetic prototype", False, has(r"diegetic")),
        Check("conversation_piece", "frames the artifact as a prop / conversation piece that provokes questions", False,
              has(r"conversation piece|\bprops?\b|provocation|provok\w+")),
        Check("mundane", "sets it in mundane, everyday use", False, has(r"mundane|everyday|ordinary|vernacular")),
        Check("users_word", "calls people 'users' (Bleecker: design makes things for people)", True, has(r"\busers?\b")),
        Check("prediction_claim", "presents the fiction as what will happen", True,
              has_unnegated(r"\bwill (?:happen|become the norm)\b|\bin the future, (?:all|every)\b")),
    ],
    "fdbx-horizon-scanning": [
        Check("scoping_question", "starts from a scoping question", False, has(r"scoping question|focal question|scan(?:ning)? question")),
        Check("categories", "organises signals by PESTLE / STEEP", False, has(r"PESTLE|STEEP|PEST\b")),
        Check("natural_agenda", "clusters signals by themes that emerge (natural agenda)", False,
              has(r"natural agenda|emergent themes?|cluster\w*")),
        # The toolkit's own list (p. 39), not the generic "weak signal" vocabulary.
        Check("signal_types", "types signals with the toolkit's list (at least three of: established trend, expected development, emerging issue, risk/opportunity, possible event)", False,
              count_at_least([r"established trends?", r"expected developments?", r"emerging issues?", r"risks? (?:or|and|/) opportunit", r"possible (?:future )?events?"], 3)),
        Check("impact_likelihood", "rates impact and likelihood", False, has(r"impact[^\n]{0,40}(?:likelihood|probability)|(?:likelihood|probability)[^\n]{0,40}impact")),
        Check("newness", "asks how new each signal is to the organisation", False, has(r"new to (?:the|your|our) organi|newness|already (?:well )?understood")),
        # The runner has no search tool and no prompt contains a link, so any URL
        # in an output was produced from model memory.
        Check("links", "gives source links (with no search tool: invented)", True, has(r"https?://")),
        Check("named_sources", "names specific reports, companies or studies as sources", True,
              has(r"\b(?:report|study|survey) (?:by|from)\b|according to")),
    ],
}

# Judgement calls a regex cannot make. Read these per output and record the verdicts
# in docs/baseline-probe-batch-1.md so the reading can be audited.
MANUAL_CHECKS = {
    "fdbx-causal-layered-analysis": ["who acts differs by layer", "two or more discourses that constitute different problems", "scenarios differ in kind per layer"],
    "fdbx-four-futures": ["futures differ in underlying logic, not one variable", "collapse presented with people who do well", "any ranking language is genuine ranking"],
    "fdbx-three-horizons": ["horizons co-exist rather than succeed each other", "H1 treated as more than 'bad'", "pockets of the future are concrete existing examples"],
    "fdbx-futures-triangle": ["weights differ per image", "pushes carry sources or are marked as assumptions"],
    "fdbx-futures-wheel": ["rings completed in turn, not linear chains", "consequences go beyond the obvious domain", "product implications traced to specific consequences"],
    "fdbx-futures-cone": ["classes treated as nested, not separate boxes", "preposterous futures taken seriously", "which class the current strategy assumes"],
    "fdbx-backcasting": ["steps actually worked backwards from the end state", "end state specific enough to backcast from", "actors outside the team named"],
    "fdbx-design-fiction": ["artifact is shown, not described", "the fiction raises questions rather than selling the product", "tensions or downsides visible in the artifact"],
    "fdbx-horizon-scanning": ["signals are real and checkable", "invented statistics or sources", "supplied signals used without padding"],
}

TYPED_ROW = re.compile(r"^\|.*\|[`*\s]*(?:assumption|sourced|user[-\u2010\u2011\u2013 ]supplied)[`*\s]*\|", I | re.M)

GLOBAL_CHECKS = [
    Check("numeric_claims", "states numeric claims (percent or money figures)", True, has(NUMERIC_CLAIM)),
    Check("typed_evidence", "has Evidence Ledger rows typed assumption / sourced / user-supplied", False,
          lambda text: bool(TYPED_ROW.search(text))),
    Check("handoff", "ends with a Handoff naming a next method", False, has(r"(?m)^#+\s*handoff")),
    # No probe prompt contains a link and the runner has no search tool, so a row
    # typed `sourced` can only be model memory presented as a source.
    Check("sourced_rows", "types a claim `sourced` (none can be: no links, no search)", True,
          has(r"(?im)^\|[^\n]*\|[`*\s]*sourced[`*\s]*\|")),
    Check("sourced_no_url", "types a claim `sourced` with no URL in the row", True,
          lambda text: any("http" not in row for row in re.findall(r"(?im)^\|[^\n]*\|[`*\s]*sourced[`*\s]*\|[^\n]*$", text))),
]


# Accept formatting variants the model uses for the same three types: backticks,
# bold, and non-breaking or en-dash hyphens ("user‑supplied"). Anything else in
# the Type column is an invented type.
VALID_TYPE = re.compile(r"^[`*\s]*(?:assumption|sourced|user[-\u2010\u2011\u2013 ]supplied)[`*\s]*$", I)


def ledger_types(text: str) -> tuple[int, int]:
    """(rows, correctly typed rows) in the last Evidence Ledger table of an output."""
    heads = [m.start() for m in re.finditer(r"(?im)^#+\s*evidence ledger", text)]
    if not heads:
        return 0, 0
    section = text[heads[-1]:]
    nxt = re.search(r"(?m)^#+\s", section[5:])
    section = section[: nxt.start() + 5] if nxt else section
    rows = [l for l in section.splitlines() if l.startswith("|") and not set(l.replace("|", "").strip()) <= set("-: ")][1:]
    types = [cells[1].strip() for cells in (l.strip().strip("|").split("|") for l in rows) if len(cells) > 1]
    return len(types), sum(bool(VALID_TYPE.match(t)) for t in types)


def load(arm: str, run: str | None = None) -> dict[str, list[dict]]:
    """Generations for one arm. With `run`, only the tasks in that run's manifest,
    which matters once a SKILL.md has changed and the cache holds both versions."""
    keys = None
    if run:
        manifest = json.loads((EVAL_DIR / "runs" / f"{run}.json").read_text())
        keys = {t["key"] for t in manifest["tasks"] if t["arm"] == arm}
    docs: dict[str, list[dict]] = defaultdict(list)
    for path in sorted(CACHE_DIR.glob("*.json")):
        if keys is not None and path.stem not in keys:
            continue
        doc = json.loads(path.read_text())
        if doc.get("arm") == arm:
            docs[doc["skill"]].append(doc)
    return docs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", default="without_skill", choices=["without_skill", "with_skill", "compare"])
    parser.add_argument("--run", action="append", default=[],
                        help="run id(s) from eval-framework/runs/ to take with_skill outputs from; repeatable")
    args = parser.parse_args()
    if args.arm == "compare":
        return compare(args.run)
    docs = load(args.arm)
    if not docs:
        sys.exit(f"no {args.arm} generations in {CACHE_DIR}")

    for skill in sorted(docs):
        items = docs[skill]
        print(f"\n## {skill}  ({len(items)} outputs, {args.arm})\n")
        print("| Check | Hits | Reading |")
        print("|---|---|---|")
        for check in CHECKS.get(skill, []) + GLOBAL_CHECKS:
            hits = [d for d in items if check.fn(d["output"])]
            reading = "failure the skill targets" if check.failure_if_true else "behaviour the skill requires"
            print(f"| {check.question} | {len(hits)}/{len(items)} | {reading} |")
        numeric = [len(re.findall(NUMERIC_CLAIM, d["output"], I)) for d in items]
        words = [len(d["output"].split()) for d in items]
        print(f"\nNumeric claims per output: {sorted(numeric)}")
        print(f"Words per output: {sorted(words)}")
        print("Read manually: " + "; ".join(MANUAL_CHECKS.get(skill, [])))
    return 0


def compare(runs: list[str]) -> int:
    base = load("without_skill")
    skill: dict[str, list[dict]] = defaultdict(list)
    if runs:
        # Later runs replace earlier ones skill by skill, so "old run + re-run of
        # three skills" compares the current version of every skill.
        for run in runs:
            for name, items in load("with_skill", run).items():
                skill[name] = items
    else:
        skill = load("with_skill")
    for name in sorted(set(base) | set(skill)):
        b, s = base.get(name, []), skill.get(name, [])
        print(f"\n## {name}  (baseline {len(b)}, with skill {len(s)})\n")
        print("| Check | Baseline | With skill | Reading |")
        print("|---|---|---|---|")
        for check in CHECKS.get(name, []) + GLOBAL_CHECKS:
            hb = sum(bool(check.fn(d["output"])) for d in b)
            hs = sum(bool(check.fn(d["output"])) for d in s)
            reading = "failure" if check.failure_if_true else "required"
            print(f"| {check.question} | {hb}/{len(b)} | {hs}/{len(s)} | {reading} |")
        wb = sorted(len(d["output"].split()) for d in b)
        ws = sorted(len(d["output"].split()) for d in s)
        med = lambda xs: xs[len(xs) // 2] if xs else 0
        print(f"\nMedian words: baseline {med(wb)}, with skill {med(ws)}")
        rows = [ledger_types(d["output"]) for d in s]
        total, valid = sum(r for r, _ in rows), sum(v for _, v in rows)
        full = sum(1 for r, v in rows if r and r == v)
        if total:
            print(f"Ledger rows correctly typed: {valid}/{total} ({valid / total:.0%}); outputs fully typed {full}/{len(s)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
