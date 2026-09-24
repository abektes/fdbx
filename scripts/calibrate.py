#!/usr/bin/env python3
"""Measure Jev against hand labels before trusting any conformance number.

The gate: agreement must meet or beat 81%, the cross-judge agreement already
accepted between Claude Sonnet 4.6 and Gemini 2.5 Pro in RESULTS.md. Below that,
Jev is demoted from judge to triage.

Reports agreement at the current thresholds, the separation between positive and
negative cases, and any case where the model contradicts the human label -- those
are read individually, never just counted.

    python3 scripts/calibrate.py --skills value-dams-and-flows
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from box import BOX, SKILLS_DIR  # noqa: E402
from conformance import EVAL_DIR, REPO, ask_jev, load_env  # noqa: E402,F401

GATE = 0.81
# Agreement is measured only on cases the judge decides. A judge that sends most
# cases to review can post 100% agreement while being useless -- the first version
# of this gate passed a closing_synthesis judge that decided 5 of 11 cases with a
# +0.07 margin. So indecision is gated too.
MAX_REVIEW_SHARE = 0.25
MIN_MARGIN = 0.30


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills", required=True)
    parser.add_argument("--yes", type=float, default=0.70)
    parser.add_argument("--no", type=float, default=0.30)
    args = parser.parse_args()

    api_key = load_env().get("TYPESAFE_API_KEY")
    if not api_key:
        sys.exit("TYPESAFE_API_KEY not found")

    agree = total = review = 0
    disagreements: list[str] = []
    spread: dict[str, tuple[list[float], list[float]]] = {}

    for short in (s.strip() for s in args.skills.split(",")):
        cal_path = EVAL_DIR / "calibration" / f"{short}.json"
        spec_path = SKILLS_DIR / f"{BOX}-{short}" / "conformance.json"
        cases = json.loads(cal_path.read_text())["cases"]
        spec = {c["id"]: c for c in json.loads(spec_path.read_text())["semantic"]}

        for crit_id, items in cases.items():
            criterion = spec[crit_id]
            texts = [c["text"] for c in items]
            labels = [c["label"] for c in items]

            # Calibrate in the same state layout the scorer uses. Section-, tail- and
            # document-scoped criteria send one text per request in production;
            # batching their calibration cases together contaminates each answer
            # with its neighbours and measures a judge that is never deployed.
            single = any(k in criterion for k in ("scope", "section"))
            batches = [[t] for t in texts] if single else [texts]
            # `with_prompt` criteria see the brief as its own state field, as in scoring.
            brief = {"brief": items[0]["brief"]} if criterion.get("with_prompt") else {}
            scores = []
            for batch in batches:
                questions = {
                    f"item_{i}": {
                        "type": "noul",
                        "instructions": criterion["instructions"].replace("{i}", str(i)),
                        "criteria": criterion["criteria"],
                    }
                    for i in range(len(batch))
                }
                answers = ask_jev({"items": batch} | brief, questions, api_key)["answers"]
                scores += [answers[f"item_{i}"]["noul"] for i in range(len(batch))]

            pos = [s for s, l in zip(scores, labels) if l]
            neg = [s for s, l in zip(scores, labels) if not l]
            spread[crit_id] = (pos, neg)

            print(f"\n--- {crit_id}")
            for text, label, score in zip(texts, labels, scores):
                if score >= args.yes:
                    verdict = True
                elif score < args.no:
                    verdict = False
                else:
                    verdict = None

                total += 1
                if verdict is None:
                    review += 1
                    mark = "review"
                elif verdict == label:
                    agree += 1
                    mark = "ok"
                else:
                    mark = "MISMATCH"
                    disagreements.append(f"{crit_id}: human={label} jev={score:.2f} :: {text[:90]}")

                snippet = text.replace("\n", " ")[:62]
                print(f"   {score:.2f}  human={str(label):5s} {mark:9s} {snippet}")

    print("\n" + "=" * 74)
    for crit_id, (pos, neg) in spread.items():
        lo_pos = min(pos) if pos else float("nan")
        hi_neg = max(neg) if neg else float("nan")
        margin = lo_pos - hi_neg
        flag = "separated" if margin > 0 else "OVERLAP"
        print(f"{crit_id:28s} worst positive {lo_pos:.2f} | best negative {hi_neg:.2f} "
              f"| margin {margin:+.2f}  {flag}")

    decided = total - review
    rate = agree / decided if decided else 0.0
    print("=" * 74)
    print(f"cases {total}, decided {decided}, sent to review {review}")
    print(f"agreement on decided cases: {agree}/{decided} = {rate:.0%}  (gate {GATE:.0%})")

    if disagreements:
        print("\nMISMATCHES — read each one, do not just count them:")
        for line in disagreements:
            print(f"  - {line}")

    review_share = review / total if total else 1.0
    thin = [cid for cid, (pos, neg) in spread.items()
            if pos and neg and min(pos) - max(neg) < MIN_MARGIN]
    print(f"review share: {review_share:.0%}  (limit {MAX_REVIEW_SHARE:.0%})")
    if thin:
        print(f"thin margin (< {MIN_MARGIN:+.2f}): {', '.join(thin)}")

    if rate < GATE:
        verdict = "FAIL — agreement below gate; demote Jev to triage"
    elif review_share > MAX_REVIEW_SHARE:
        verdict = "FAIL — judge too indecisive to act on; rewrite the criterion"
    elif thin:
        verdict = "FAIL — positives and negatives barely separate; rewrite the criterion"
    elif disagreements:
        verdict = "PASS (with mismatches to review)"
    else:
        verdict = "PASS — Jev can act as judge"
    print("\nRESULT:", verdict)
    return 0 if verdict.startswith("PASS") else 1


if __name__ == "__main__":
    sys.exit(main())
