#!/usr/bin/env python3
"""Compare two conformance runs check by check.

A skill edit is only credited with a change when the before/after difference is
unlikely to be sampling noise. With a handful of generations per side that bar is
real: 5/9 -> 7/9 is well within what two identical skills would produce. Each row
carries a two-sided Fisher exact p-value on pass vs not-pass.

    python3 scripts/compare_scores.py before.json after.json
"""

from __future__ import annotations

import argparse
import json
import sys
from math import comb

from box import short


def fisher_two_sided(a: int, b: int, c: int, d: int) -> float:
    """p-value for the 2x2 table [[a, b], [c, d]] (pass/other x before/after)."""
    row1, row2, col1, n = a + b, c + d, a + c, a + b + c + d

    def p(x: int) -> float:
        return comb(row1, x) * comb(row2, col1 - x) / comb(n, col1)

    observed = p(a)
    lo, hi = max(0, col1 - row2), min(row1, col1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= observed * (1 + 1e-9)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args()

    before = json.load(open(args.before))["rates"]
    after = json.load(open(args.after))["rates"]

    print(f"{'check':38s} {'before':>8} {'after':>8}   p      verdict")
    for skill in sorted(set(before) | set(after)):
        print(f"\n{short(skill)}")
        checks = list(dict.fromkeys([*before.get(skill, {}), *after.get(skill, {})]))
        for cid in checks:
            b = before.get(skill, {}).get(cid)
            a = after.get(skill, {}).get(cid)
            if not b or not a:
                print(f"  {cid:36s} {'-':>8} {'-':>8}   only in one run")
                continue
            bn, an = sum(b.values()), sum(a.values())
            bp, ap = b["pass"], a["pass"]
            p = fisher_two_sided(bp, bn - bp, ap, an - ap)
            if bp == ap and bn == an:
                verdict = ""
            elif p < 0.05:
                verdict = "IMPROVED" if ap / an > bp / bn else "REGRESSED"
            else:
                verdict = "up (noise-level)" if ap / an > bp / bn else "down (noise-level)"
            print(f"  {cid:36s} {bp:>3}/{bn:<4} {ap:>3}/{an:<4} {p:5.2f}   {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
