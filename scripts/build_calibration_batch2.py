#!/usr/bin/env python3
"""Write the hand-labelled calibration cases for backcasting and horizon-scanning.

Labels are the skills' author's (Claude), 2026-09-24, and need a second reader.
Positives are real skill or baseline text. Negatives are real where the plain
model produced one; where no output failed that way, a constructed case is used
and marked as such, so a reader can discount it.

    python3 scripts/build_calibration_batch2.py && python3 scripts/calibrate.py --skills backcasting,horizon-scanning
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from box import EVAL_DIR, SKILLS_DIR  # noqa: E402
from conformance import enumerate_items, section_text  # noqa: E402

C = "constructed to match the criterion's false description; no real output failed this way"
NOTE = ("Hand labels by the skills' author (Claude), 2026-09-24. Positives are real with-skill or "
        "baseline text; negatives are real where the plain model produced one, else constructed and "
        "marked. Needs a second reader.")


def docs(run: str, skill: str, arm: str) -> list[dict]:
    m = json.loads((EVAL_DIR / "runs" / f"{run}.json").read_text())
    return [json.loads((EVAL_DIR / "generations" / f"{t['key']}.json").read_text())
            for t in m["tasks"] if t["skill"] == skill and t["arm"] == arm]


def case(label: bool, text: str, note: str) -> dict:
    assert text.strip(), note
    return {"label": label, "text": text, "note": note}


def main() -> int:
    bc = json.loads((SKILLS_DIR / "fdbx-backcasting" / "conformance.json").read_text())
    hs = json.loads((SKILLS_DIR / "fdbx-horizon-scanning" / "conformance.json").read_text())
    BW = docs("20260924T192125Z", "fdbx-backcasting", "with_skill")
    BB = docs("20260924T183759Z", "fdbx-backcasting", "without_skill")
    HW = docs("20260924T204056Z", "fdbx-horizon-scanning", "with_skill")
    HB = docs("20260924T183759Z", "fdbx-horizon-scanning", "without_skill")

    losers = [c for d in BW for c in enumerate_items(d["output"], bc["enumerators"]["in_control_losers"])]
    infl = [c for d in BW for c in enumerate_items(d["output"], bc["enumerators"]["influence"])]
    base_close = [section_text(d["output"], "conclusion") for d in BB]
    base_close = [s for s in base_close if s.strip()]

    backcasting = {"_note": NOTE, "cases": {
        "end_state_checkable": [
            case(True, section_text(BW[0]["output"], "preferred future"), "with-skill"),
            case(True, section_text(BW[4]["output"], "preferred future"), "with-skill"),
            case(True, section_text(BB[0]["output"], "vision"), "baseline, but concrete: use cycles, tracking, return channels"),
            case(True, section_text(BB[7]["output"], "desired future"), "baseline, concrete: 24/7 carbon-free energy, carbon-aware scheduling"),
            case(False, "## The Preferred Future in 2035\n\nIn 2035 we are recognised as the most accessible and inclusive transit network in the country. Accessibility is part of our DNA, customers feel welcome and valued, and we lead the industry in inclusive experience.", C),
            case(False, "## The Preferred Future in 2040\n\nOur packaging reflects our values. We are a sustainability leader, customers love our commitment to the planet, and circularity is at the heart of everything we do.", C),
            case(False, "## The Preferred Future in 2032\n\nWe have become a truly green software company with a best-in-class approach to sustainability and a culture of climate responsibility across all teams.", C),
        ],
        "loser_named": [
            *[case(True, losers[i], "with-skill") for i in (2, 9, 19, 25)],
            case(False, "Benefits: all stakeholders — customers, the company and the environment. No one loses out.", C),
            case(False, "Benefits: consumers, retailers, the company. Loses out: n/a", C),
            case(False, "Benefits: everyone. Some stakeholders may be affected.", C),
        ],
        "influence_concrete": [
            *[case(True, infl[i], "with-skill") for i in (2, 7, 11, 15)],
            case(False, "Monitor regulatory developments and stay informed about policy changes.", C),
            case(False, "Advocate for change where possible.", C),
            case(False, "Hope that the government introduces a national deposit return scheme.", C),
        ],
        "handoff_why": [
            case(True, section_text(BW[0]["output"], "handoff"), "with-skill"),
            case(True, section_text(BW[5]["output"], "handoff"), "with-skill"),
            case(True, section_text(HW[3]["output"], "handoff"), "with-skill (horizon scan)"),
            case(False, base_close[0], "baseline conclusion: names no next method"),
            case(False, base_close[1], "baseline conclusion: names no next method"),
            case(False, "## Handoff\n\n**Assumptions surfaced:** reuse rates, retailer cooperation.\n**Open decisions:** which category to pilot first.\n**Suggested next method:** fdbx-three-horizons.", C + " (method named, no reason)"),
        ],
    }}

    prompt = next(e["prompt"] for e in json.loads((SKILLS_DIR / "fdbx-horizon-scanning" / "evals" / "evals.json").read_text())["evals"]
                  if e["name"].startswith("library"))
    # `with_prompt` criteria get the brief as a separate state field.
    wp = lambda v: v  # noqa: E731
    sig = [c for d in HW for c in enumerate_items(d["output"], hs["enumerators"]["signals_with_source"])]
    pick = lambda pat: next(s for s in sig if re.search(pat, s))  # noqa: E731
    drivers = []
    for d in HW[:3]:
        drivers.append(enumerate_items(d["output"], hs["enumerators"]["drivers"])[0])
    trend_doc = next(d["output"] for d in HB if "**Autonomous delivery**" in d["output"])

    def para(title: str) -> str:
        m = re.search(r"\*\*" + re.escape(title) + r"\*\*[ \t]*\n([^\n]+)", trend_doc)
        return f"**{title}**\n{m.group(1)}"

    base_hs_close = next(s for d in HB if (s := section_text(d["output"], "conclusion")).strip())

    scanning = {"_note": NOTE, "cases": {
        # The toolkit's scan is "an external event or emerging trend" (glossary,
        # p. 114), so a forecast attributed to a named source is a positive.
        "signal_observed": [
            case(True, pick("Roquette"), "with-skill, sourced"),
            case(True, pick(r"\b22\s?%"), "with-skill, sourced"),
            case(True, pick("power tools"), "with-skill, user-supplied"),
            case(True, pick(r"2\.33"), "with-skill: a forecast attributed to its report"),
            case(True, pick("Super-foods"), "with-skill: a report's forecast, attributed in the Source cell"),
            case(True, pick("Deliveroo report predicts"), "with-skill: a report's forecast"),
            case(True, pick("publisher is testing a subscription‑only ebook model for libraries, replacing"), "with-skill: user-supplied, source given as staff"),
            case(True, pick("aspirational"), "with-skill: a published view, source given as a site name"),
            case(False, "Consumers increasingly expect zero-friction, predictive services.\nSource: (none)", "baseline trend statement; the baseline cited nothing"),
            case(False, "Large language models are moving from chat to action; AI agents will negotiate orders on users' behalf.\nSource: (none)", "baseline trend statement"),
            case(False, "City X mandates 15-minute delivery zones for all couriers\nSource: Link to council press release", "with-skill (earlier run): illustrative example row"),
            case(False, "Gig-worker platforms are increasingly automating dispatch decisions.\nSource: general industry knowledge", C),
        ],
        "user_signal_unembellished": [
            case(True, wp("A nearby public library has begun lending power tools to patrons."), "with-skill"),
            case(True, wp("A council report shows overall footfall is down but Wi‑Fi sessions are up."), "with-skill"),
            case(True, wp("A publisher is testing a subscription‑only ebook model for libraries, replacing perpetual purchase with recurring fees."), "with-skill; 'replacing' is interpretation, not a new fact"),
            case(False, wp("A recent local authority performance report indicates a year‑on‑year decline in physical visits (12%) but a 20% increase in logged Wi‑Fi sessions."), "baseline: invented 12% and 20%"),
            case(False, wp("A recent council report shows footfall is down 12% year‑on‑year, but recorded Wi‑Fi sessions have increased by 34%."), "baseline: invented 12% and 34%"),
            case(False, wp("Leeds Central Library has begun lending power tools, according to a 2025 CILIP briefing."), C),
        ],
        "driver_actionable": [
            *[case(True, t, "with-skill") for t in drivers],
            case(False, para("Autonomous delivery"), "baseline trend paragraph: describes, no action"),
            case(False, para("Smart kitchen and IoT integration"), "baseline trend paragraph"),
            case(False, para("Spatial computing and AR/VR"), "baseline trend paragraph"),
        ],
        "handoff_why": [
            case(True, section_text(HW[0]["output"], "handoff"), "with-skill"),
            case(True, section_text(HW[5]["output"], "handoff"), "with-skill"),
            case(False, base_hs_close, "baseline conclusion: names no next method"),
            case(False, "## Handoff\n\n**Assumptions surfaced:** ratings are provisional.\n**Open decisions:** which driver to fund.\n**Suggested next method:** further research.", C),
        ],
    }}

    for c in scanning["cases"]["user_signal_unembellished"]:
        c["brief"] = prompt

    out = EVAL_DIR / "calibration"
    out.mkdir(exist_ok=True)
    for name, cal in (("backcasting", backcasting), ("horizon-scanning", scanning)):
        (out / f"{name}.json").write_text(json.dumps(cal, indent=1, ensure_ascii=False))
        print(name, {k: f"{sum(c['label'] for c in v)}+/{sum(not c['label'] for c in v)}-"
                     for k, v in cal["cases"].items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
