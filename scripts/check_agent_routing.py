#!/usr/bin/env python3
"""Check that the Futures Design Specialist agent routes situations to the right method.

Runs the agent headlessly through the Claude Code CLI with this repo loaded as a
plugin (session only; nothing is installed), asks it which method it would use
first without running it, and checks the first fdbx method its answer names.
The traps check redirects: a request for a prediction or for market figures
must not be answered as asked.

Uses your Claude Code login. Inside a Claude Code session the host's auth
variables are cleared first, because a child CLI cannot use them.

    python3 scripts/check_agent_routing.py
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import subprocess
import sys

from box import REPO

AGENT = "fdbx:futures-design-specialist"
ASK = " Which fdbx method would you use first and why? Answer in at most four sentences; do not run it yet."

METHODS = {
    "horizon-scanning": r"horizon scanning|horizon-scanning",
    "causal-layered-analysis": r"causal layered analysis|causal-layered-analysis|\bCLA\b",
    "futures-triangle": r"futures triangle|futures-triangle",
    "four-futures": r"four futures|four-futures|four generic futures",
    "three-horizons": r"three horizons|three-horizons",
    "backcasting": r"backcast",
}

# (situation, expected first method, extra pattern the answer must match or None)
CASES = [
    ("Our staff noticed teenagers using study rooms for quiet gaming and a neighbouring library lending power tools. We want to know what these add up to.",
     "horizon-scanning", None),
    ("We run a food delivery app and want to know what we should be watching over the next ten years.",
     "horizon-scanning", None),
    ("The brief says 'design a feature to reduce teen screen time' and it feels like we keep designing the same lock-out tool.",
     "causal-layered-analysis", None),
    ("We're a city mobility team. Everyone has a different picture of 2040 and we don't know which future our current strategy is actually serving.",
     "futures-triangle", None),
    ("Our banking app roadmap assumes steady growth to 2050. What if the future isn't like that?",
     "four-futures", None),
    ("Our regional newspaper's print model is dying and we have ten pilots running. Which of them actually help the next model emerge?",
     "three-horizons", None),
    ("We committed to reusable packaging for every product by 2040 and our roadmap only covers the next two years.",
     "backcasting", None),
    ("We are afraid our energy app ends up enabling a surveillance-heavy grid by 2040. How would we see that coming and stop it?",
     "backcasting", None),
    ("Which scenario for the future of university learning is most likely? Just tell us.",
     "four-futures", r"won.t rank|not rank|no .{0,20}(?:method|one) can|can.t (?:honestly )?(?:tell|predict)|isn.t a (?:forecast|prediction)|not (?:a )?predict"),
    ("Give us the market size and growth rate for fashion resale for our strategy deck.",
     "horizon-scanning", r"memory|search|source|won.t (?:produce|give|invent)|not (?:from|invent)"),
]

HOST_VARS = ["ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL", "ANTHROPIC_MODEL", "ANTHROPIC_REASONING_MODEL",
             "ANTHROPIC_DEFAULT_OPUS_MODEL", "ANTHROPIC_DEFAULT_SONNET_MODEL", "ANTHROPIC_DEFAULT_HAIKU_MODEL",
             "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_CHILD_SESSION"]


def ask(situation: str) -> str:
    env = {k: v for k, v in os.environ.items() if k not in HOST_VARS}
    out = subprocess.run(
        ["claude", "-p", "--plugin-dir", str(REPO), "--agent", AGENT, "--max-turns", "3", situation + ASK],
        capture_output=True, text=True, timeout=300, env=env, cwd="/tmp")
    return (out.stdout or out.stderr).strip()


def first_method(answer: str) -> str | None:
    hits = [(m.start(), name) for name, rx in METHODS.items() for m in [re.search(rx, answer, re.I)] if m]
    return min(hits)[1] if hits else None


def main() -> int:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        answers = list(pool.map(ask, [c[0] for c in CASES]))
    passed = 0
    for (situation, expected, extra), answer in zip(CASES, answers):
        got = first_method(answer)
        ok = got == expected and (extra is None or re.search(extra, answer, re.I))
        passed += bool(ok)
        print(f"[{'PASS' if ok else 'FAIL'}] expected {expected}, first named {got}")
        print(f"       {situation[:90]}")
        print(f"       -> {re.sub(r'\\s+', ' ', answer)[:260]}\n")
    print(f"{passed}/{len(CASES)} routed as expected")
    return 0 if passed == len(CASES) else 1


if __name__ == "__main__":
    sys.exit(main())
