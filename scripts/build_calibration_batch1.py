#!/usr/bin/env python3
"""Write the hand-labelled calibration cases for the four batch 1 skills.

Labels are the skills' author's (Claude), 2026-09-25, and need a second reader.
Positives are real outputs. Negatives are real where some output failed that
way, and otherwise constructed and marked, so a reader can discount them.

    python3 scripts/build_calibration_batch1.py
    python3 scripts/calibrate.py --skills causal-layered-analysis,futures-triangle,four-futures,three-horizons
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from box import EVAL_DIR, SKILLS_DIR  # noqa: E402
from build_calibration_batch2 import C, NOTE, case, docs  # noqa: E402
from conformance import enumerate_items, section_text  # noqa: E402

RUN = "20260924T192125Z"  # with-skill outputs from the current SKILL.md
BASE = "20260924T112516Z"  # without-skill baseline


def rubric(skill: str) -> dict:
    return json.loads((SKILLS_DIR / f"fdbx-{skill}" / "conformance.json").read_text())


def items(outputs: list[dict], spec: dict, name: str) -> list[str]:
    return [i for d in outputs for i in enumerate_items(d["output"], spec["enumerators"][name])]


def handoffs(outputs: list[dict], base: list[dict], method: str) -> list[dict]:
    closing = [s for d in base if (s := section_text(d["output"], "conclusion|next steps", "last")).strip()]
    return [
        case(True, section_text(outputs[0]["output"], "handoff"), "with-skill"),
        case(True, section_text(outputs[4]["output"], "handoff"), "with-skill"),
        case(False, closing[0], "baseline closing section: names no next method"),
        case(False, f"## Handoff\n\n**Assumptions surfaced:** the brief's framing.\n**Open decisions:** which option to pursue.\n**Suggested next method:** {method}.", C + " (method named, no reason)"),
    ]


def main() -> int:
    cal: dict[str, dict] = {}

    # ------------------------------------------------------------ CLA
    s = rubric("causal-layered-analysis")
    W, B = docs(RUN, "fdbx-causal-layered-analysis", "with_skill"), docs(BASE, "fdbx-causal-layered-analysis", "without_skill")
    wv = items(W, s, "worldviews")
    ref = items(W, s, "reframed")
    cal["causal-layered-analysis"] = {"_note": NOTE, "cases": {
        "worldview_constitutes_problem": [
            *[case(True, wv[i], "with-skill") for i in (0, 1, 4)],
            case(False, "- **Parents** — want their teenagers to spend less time on phones.", C),
            case(False, "- **Managers** — are concerned about engagement scores.", C),
            case(False, "- **A techno-optimist view** — technology is generally good and will keep improving.", C + " (a view with no problem stated)"),
        ],
        "scenarios_differ_in_kind": [
            case(True, section_text(W[0]["output"], "scenarios"), "with-skill"),
            case(True, section_text(W[3]["output"], "scenarios"), "with-skill"),
            case(True, section_text(W[6]["output"], "scenarios"), "with-skill"),
            case(False, "## Scenarios by Layer\n\n1. **Low adoption** — 10% of teams use the new Team Space; little changes.\n2. **Moderate adoption** — 40% use it weekly; some teams feel more connected.\n3. **High adoption** — 75% use it daily; connection scores rise.\n4. **Full adoption** — every team runs its rituals in the Team Space.", C),
            case(False, "## Scenarios by Layer\n\n1. **Small fix** — a screen-time dashboard reduces use slightly.\n2. **Bigger fix** — stricter limits reduce use more.\n3. **Strong fix** — lockouts after one hour.\n4. **Maximum fix** — phones are locked at school and at night.", C),
        ],
        "reframed_is_brief": [
            *[case(True, ref[i], "with-skill") for i in (0, 3, 6)],
            case(False, "**Reframed brief:** The deeper issue is that the organisation treats connection as a metric rather than a relationship, and this worldview shapes every intervention it tries.", C + " (analysis, not a brief)"),
            case(False, "### Reframed Brief\n\nScreen time is a symptom of wider cultural anxieties about adolescence and technology, which are rooted in a purity myth.", C + " (analysis, not a brief)"),
        ],
        "handoff_why": handoffs(W, B, "fdbx-four-futures"),
    }}

    # ------------------------------------------------------------ Triangle
    s = rubric("futures-triangle")
    W, B = docs(RUN, "fdbx-futures-triangle", "with_skill"), docs(BASE, "fdbx-futures-triangle", "without_skill")
    sc = items(W, s, "scenarios")
    cal["futures-triangle"] = {"_note": NOTE, "cases": {
        "plausible_justified": [
            *[case(True, section_text(W[i]["output"], "interaction"), "with-skill") for i in (0, 3, 6)],
            case(False, "## Interaction\n\n**Plausible future:** Green Livable Neighbourhoods.\n**Contested images:** Seamless Transit City and Gaia.\n**Unchosen pushes:** ageing population.", C + " (named, not justified)"),
            case(False, "## Interaction\n\n**Plausible future:** Hyper-efficient utility, because the market for delivery keeps growing quickly.\n**Contested images:** ...", C + " (push only)"),
        ],
        "scenario_grounded": [
            *[case(True, sc[i], "with-skill") for i in (0, 5, 9)],
            case(False, "1. **The Quiet City** — By 2040 most people work near home, streets are calmer and the mobility app is used mainly for weekend trips.", C),
            case(False, "2. **Fast Lane** — Deliveries arrive within ten minutes everywhere and customers expect instant everything.", C),
        ],
        "handoff_why": handoffs(W, B, "fdbx-four-futures"),
    }}

    # ------------------------------------------------------------ Four futures
    W, B = docs(RUN, "fdbx-four-futures", "with_skill"), docs(BASE, "fdbx-four-futures", "without_skill")
    cal["four-futures"] = {"_note": NOTE, "cases": {
        "distinct_logics": [
            *[case(True, section_text(W[i]["output"], "at a glance"), "with-skill") for i in (0, 3, 6)],
            case(False, "## The Four Futures at a Glance\n\n| Future | Generic type | Underlying logic |\n|---|---|---|\n| Boom | Continued Growth | Heat pumps reach 90% of homes |\n| Slump | Collapse | Heat pumps reach 20% of homes |\n| Steady | Discipline | Heat pumps reach 50% of homes |\n| Leap | Transformation | Heat pumps reach 100% of homes |", C),
            case(False, "## The Four Futures at a Glance\n\n| Future | Generic type | Underlying logic |\n|---|---|---|\n| Digital max | Continued Growth | All teaching online |\n| Digital min | Collapse | Almost no teaching online |\n| Digital mid | Discipline | Half of teaching online |\n| Digital plus | Transformation | All teaching online, with VR |", C),
        ],
        "collapse_positive": [
            *[case(True, section_text(W[i]["output"], "collapse"), "with-skill") for i in (0, 4)],
            case(True, section_text(B[0]["output"], "collapse"), "baseline, which also shows people doing well"),
            case(False, "## Future 2: The Dark Grid — Collapse\n\nBy 2050 the grid has failed. Homes go without heat for weeks, food spoils, hospitals run on failing generators and crime rises. Communities fracture and people struggle to survive from day to day.", C),
            case(False, "## Future 2: Closed Doors — Collapse\n\nUniversities have shut. Graduates cannot find work, research has stopped, and young people have no path to learning. Everyone is worse off.", C),
        ],
        "handoff_why": handoffs(W, B, "fdbx-three-horizons"),
    }}

    # ------------------------------------------------------------ Three horizons
    s = rubric("three-horizons")
    W, B = docs(RUN, "fdbx-three-horizons", "with_skill"), docs(BASE, "fdbx-three-horizons", "without_skill")
    h3 = items(W[:3], s, "h3_items")  # retail: aspirations and pockets, laid out three ways
    # W[3] (newsroom #0) writes plain-text headings, so it has no sections to read.
    cal["three-horizons"] = {"_note": NOTE, "cases": {
        "h1_evidence": [
            case(True, section_text(W[0]["output"], "h1"), "with-skill"),
            case(True, section_text(W[5]["output"], "h1"), "with-skill"),
            case(True, section_text(B[1]["output"], "horizon 1|h1"), "baseline, with 'signals of decline'"),
            case(False, "## H1 — Losing Fit\n\nThe current model is outdated and under growing pressure. The world is changing fast, and the organisation needs to adapt to stay relevant.", C),
            case(False, "## H1 — Losing Fit\n\nToday's newsroom works the way it always has. It is increasingly out of step with the times and faces many challenges.", C),
        ],
        "pocket_concrete": [
            *[case(True, x, "with-skill: names a real example") for x in h3 if any(k in x for k in ("Monzo", "Starling", "Umpqua", "Capital One", "Solaris", "Railsr"))][:3],
            *[case(False, x, "with-skill aspiration item: names no existing example") for x in h3[:2] if not any(k in x for k in ("Monzo", "Starling", "Umpqua", "Capital One", "Solaris", "Railsr"))],
            case(False, "- Some banks are experimenting with community spaces in their branches.", C),
            *[case(True, x, "with-skill: named, tagged '(Assumption.)' by the model") for x in items(W[4:5], s, "h3_items") if "Manchester Mill" in x or "Berkeleyside" in x],
            *[case(False, x, "with-skill aspiration item: a vision, no named example") for x in items(W[4:5], s, "h3_items")[:1]],
            *[case(True, x, "with-skill: a vision with its named pockets nested inside") for x in items(W[5:6], s, "h3_items")[:2]],
        ],
        "dilemma_both": [
            *[case(True, section_text(W[i]["output"], "dilemma"), "with-skill") for i in (0, 4, 6)],
            case(False, "**Dilemma:** Should we keep the branches or close them and go fully digital?", C + " (either/or)"),
            case(False, "**Dilemma:** Cutting costs is the priority.", C + " (one value)"),
        ],
        "actions_by_horizon": [
            *[case(True, section_text(W[i]["output"], "^actions"), "with-skill") for i in (0, 4, 6)],
            case(False, "## Actions\n\n- Run a customer survey.\n- Set up a working group.\n- Review the budget.\n- Pilot a new app feature.", C),
            case(False, "## Actions\n\n1. Hire a head of innovation.\n2. Explore partnerships.\n3. Communicate the vision to staff.", C),
        ],
        "handoff_why": handoffs(W, B, "fdbx-four-futures"),
    }}

    out = EVAL_DIR / "calibration"
    for name, c in cal.items():
        (out / f"{name}.json").write_text(json.dumps(c, indent=1, ensure_ascii=False))
        print(name, {k: f"{sum(x['label'] for x in v)}+/{sum(not x['label'] for x in v)}-" for k, v in c["cases"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
