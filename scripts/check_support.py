#!/usr/bin/env python3
"""Does each cited source say what the output claims it says? For --web-search runs.

check_links.py asks whether a link is real. This asks the harder question, with
the pattern from TypeSafe's "Double-checking citations" cookbook: code decides
what it can, and one Jev Choice question reads the rest.

  1. A cited URL that was not among the search results the model was given is
     `not_from_search` -- no model needed.
  2. Otherwise Jev reads the claim beside the search excerpt the model saw (the
     model saw only the excerpt, so the claim must rest on it) and answers
     supports / contradicts / says_nothing.
  3. Answers under AUTO_ACCEPT confidence are marked for a person to confirm.

The claim is the row's Signal (or Claim) cell when the URL sits in a table, else
the line that cites it. Answers are cached, so re-running costs nothing.

    python3 scripts/check_support.py <run id> [--arm with_skill]
    python3 scripts/check_support.py --calibrate
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter

from check_links import MD_URL_RE, URL_RE, norm
from conformance import EVAL_DIR, ask_jev, load_env, strip_md

AUTO_ACCEPT = 0.8  # the cookbook's starting point; lower only after reading its misses
CACHE = EVAL_DIR / "support-cache.json"
QUESTION = {
    "relation": {
        "type": "choice",
        "instructions": "How does the passage relate to the claim?",
        "criteria": {
            "supports": "The passage states the claim or directly implies that it is true, including any figures, names and dates the claim gives",
            "contradicts": "The passage states the opposite of the claim, or gives different figures, names or dates",
            "says_nothing": "The passage does not address what the claim asserts, or supports only part of it while the claim adds specifics the passage lacks",
        },
    }
}


def cited_claims(output: str) -> list[tuple[str, str]]:
    """(url, claim) pairs, one per URL per row or line.

    Read line by line rather than through parse_tables, which strips links from
    cells. In a table whose header has a Signal or Claim column, the claim is that
    cell; elsewhere it is the citing line with the link removed.
    """
    pairs: list[tuple[str, str]] = []
    lines = output.splitlines()
    claim_col: int | None = None
    for i, line in enumerate(lines):
        is_row = line.lstrip().startswith("|")
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if is_row else []
        if not is_row:
            claim_col = None
        elif i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            # Header row: remember which column holds the claim.
            claim_col = next((j for j, h in enumerate(cells)
                              if re.search(r"signal|claim", h, re.I)), None)
            continue
        urls = list(dict.fromkeys(MD_URL_RE.findall(line) or URL_RE.findall(line)))
        if not urls:
            continue
        if is_row and claim_col is not None and claim_col < len(cells):
            claim = strip_md(cells[claim_col])
        else:
            claim = line
            for url in urls:
                claim = claim.replace(url, " ")
            claim = strip_md(claim)
        if len(claim.split()) < 6:  # a bare reference-list entry makes no claim
            continue
        for url in urls:
            pairs.append((url.rstrip(".,;:"), claim))
    return pairs


def ask_cached(claim: str, passage: str, key: str, cache: dict) -> tuple[dict, int]:
    ck = hashlib.sha256(f"{claim}\x00{passage}".encode()).hexdigest()[:20]
    if ck in cache:
        return cache[ck], 0
    r = ask_jev({"claim": claim, "passage": passage}, QUESTION, key)
    cache[ck] = r["answers"]["relation"] | {"input_tokens": r["usage"]["input_tokens"]}
    CACHE.write_text(json.dumps(cache, indent=1))
    return cache[ck], r["usage"]["input_tokens"]


def calibrate(key: str, cache: dict) -> int:
    """Agreement with hand labels, by confidence threshold, under edbx's gate:
    >= 81% agreement on decided cases and <= 25% of cases left for review."""
    from calibrate import GATE, MAX_REVIEW_SHARE
    cases = json.loads((EVAL_DIR / "calibration" / "source-support.json").read_text())["cases"]
    for c in cases:
        # Rebuilt from the cached generation: copied web text is not committed.
        gen = json.loads((EVAL_DIR / "generations" / f"{c['generation']}.json").read_text())
        results = {norm(r["url"]): r for r in gen.get("search_results", [])}
        c["passage"] = "\n\n".join((results.get(norm(u)) or {}).get("content") or ""
                                    for u in c["urls"] if results.get(norm(u)))
    answers = [ask_cached(c["claim"], c["passage"], key, cache)[0] for c in cases]
    print(f"{len(cases)} hand-labelled claims, {sum(c['label'] for c in cases)} supported\n")
    print("threshold  decided  agree   review share  gate")
    best = None
    for th in (0.0, 0.6, 0.7, 0.8, 0.9):
        decided = [(c, a) for c, a in zip(cases, answers) if a["confidence"] >= th]
        agree = sum((a["choice"] == "supports") == c["label"] for c, a in decided)
        rate = agree / len(decided) if decided else 0.0
        review = 1 - len(decided) / len(cases)
        ok = rate >= GATE and review <= MAX_REVIEW_SHARE
        if ok and best is None:
            best = th
        print(f"  {th:4.1f}     {len(decided):4d}   {rate:5.0%}      {review:5.0%}        {'PASS' if ok else 'fail'}")
    print("\nMISMATCHES at threshold 0 -- read each:")
    for c, a in zip(cases, answers):
        if (a["choice"] == "supports") != c["label"]:
            print(f"  human={c['label']!s:5} jev={a['choice']} {a['confidence']:.2f}  {c['claim'][:90]}")
    return 0 if best is not None else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run", nargs="?")
    ap.add_argument("--arm", default="with_skill", choices=["with_skill", "without_skill", "both"])
    ap.add_argument("--calibrate", action="store_true",
                    help="measure Jev against eval-framework/calibration/source-support.json")
    args = ap.parse_args()

    key = load_env()["TYPESAFE_API_KEY"]
    cache = json.loads(CACHE.read_text()) if CACHE.is_file() else {}
    if args.calibrate:
        return calibrate(key, cache)
    if not args.run:
        ap.error("a run id is required unless --calibrate")
    manifest = json.loads((EVAL_DIR / "runs" / f"{args.run}.json").read_text())
    totals: dict[str, Counter] = {}
    notes: list[str] = []
    tokens = 0

    for t in manifest["tasks"]:
        if args.arm != "both" and t["arm"] != args.arm:
            continue
        d = json.loads((EVAL_DIR / "generations" / f"{t['key']}.json").read_text())
        results = {norm(r["url"]): r for r in d.get("search_results", [])}
        c = totals.setdefault(t["arm"], Counter())
        # A claim citing several links rests on all of them together; judging it
        # against each passage alone marks it unsupported by whichever says less.
        grouped: dict[str, list[str]] = {}
        for url, claim in cited_claims(d["output"]):
            grouped.setdefault(claim, []).append(url)
        for claim, urls in grouped.items():
            c["claims"] += 1
            hits = [results.get(norm(u)) for u in urls]
            url = " + ".join(urls)
            if not any(hits):
                c["not_from_search"] += 1
                notes.append(f"  not_from_search  {t['scenario']} #{t['rep']}: {claim[:110]}\n      {url}")
                continue
            passage = "\n\n".join(h.get("content") or "" for h in hits if h)
            a, used = ask_cached(claim, passage, key, cache)
            tokens += used
            c[a["choice"]] += 1
            auto = a["confidence"] >= AUTO_ACCEPT
            c["auto" if auto else "review"] += 1
            if a["choice"] != "supports" or not auto:
                notes.append(f"  {a['choice']:15s} conf {a['confidence']:.2f}  {t['scenario']} #{t['rep']}: {claim[:110]}\n      {url}")

    for arm, c in totals.items():
        print(f"\n## {arm}")
        for k in ("claims", "not_from_search", "supports", "contradicts", "says_nothing", "auto", "review"):
            print(f"  {k:16} {c[k]}")
    print(f"\n## Not verified, or verified below {AUTO_ACCEPT} confidence ({len(notes)}) -- read each")
    print("\n".join(notes) if notes else "  none")
    print(f"\nJev input tokens this invocation: {tokens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
