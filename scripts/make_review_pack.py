#!/usr/bin/env python3
"""Build a side-by-side page so a person can judge output quality, not just conformance.

The probe (docs/baseline-probe-batch-1.md) shows the skills are *followed*. Whether
their outputs are *better* needs a human reader. For each scenario this pairs one
baseline output with one with-skill output, shuffles which is A and which is B, and
writes two files to the gitignored eval-framework/review/:

  review.html   read both, answer five questions per pair, export your answers
  key.json      which side was the skill; open only after you have reviewed

Blinding is partial: with-skill outputs end with an Evidence Ledger and a Handoff,
so a careful reader can often tell them apart. The questions ask about qualities
that matter either way.

    python3 scripts/make_review_pack.py --run 20260924T115310Z --run 20260924T121528Z
    python3 scripts/make_review_pack.py --score ~/Downloads/fdbx-review-answers.json
"""

from __future__ import annotations

import argparse
import html
import json
import random
import re
import sys
from collections import Counter

from box import EVAL_DIR
from probe_baseline import load

REVIEW_DIR = EVAL_DIR / "review"
SEED = 20260924

QUESTIONS = [
    ("meeting", "Which would you rather bring into a design meeting?"),
    ("insight", "Which made you see the problem differently?"),
    ("trust", "Which is easier to trust? Can you tell fact from assumption?"),
    ("action", "Which gives you clearer next steps?"),
    ("length", "Is either longer than what it gives you?"),
]
LENGTH_CHOICES = ["A too long", "B too long", "both", "neither"]

# Passages behind claims in docs/baseline-probe-batch-1.md, so the reader can
# check the findings against the outputs themselves.
FINDINGS = [
    ("Baseline invents a 'pocket of the future' with figures", "Millfield Pilot"),
    ("Baseline invents a fact about the user's own city", "uptake has dropped by 8%"),
    ("Baseline invents a health statistic for the user's city", "2% above national average"),
    ("Baseline states an unsourced present-day figure", "foot traffic dropping 10-15%"),
    ("Baseline McKinsey-flavoured Three Horizons", "run the core"),
    ("Baseline frames Collapse positively", "Resilient Localism"),
    ("With skill: ledger admits an example is hypothetical", "Hypothetical but plausible"),
    ("With skill: body still presents that example as real", "Visit the school that already runs"),
]


# ------------------------------------------------------------------ markdown

def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", text)
    return text.replace("&lt;br&gt;", "<br>")


def md_to_html(md: str) -> str:
    """Enough Markdown for model outputs: headings, lists, tables, quotes, rules."""
    out: list[str] = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if re.fullmatch(r"[-*_]{3,}", stripped):
            out.append("<hr>")
            i += 1
        elif m := re.match(r"(#{1,6})\s+(.*)", stripped):
            level = min(len(m.group(1)) + 1, 6)
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
        elif stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in rows
                     if not set(r.replace("|", "").strip()) <= set("-: ")]
            if cells:
                head, *body = cells
                out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>")
                out += ["<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body]
                out.append("</tbody></table>")
        elif stripped.startswith(">"):
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip().lstrip(">").strip())
                i += 1
            out.append("<blockquote>" + inline(" ".join(quote)) + "</blockquote>")
        elif re.match(r"(?:[-*+]|\d+[.)])\s+", stripped):
            ordered = bool(re.match(r"\d+[.)]", stripped))
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>")
            while i < len(lines) and re.match(r"\s*(?:[-*+]|\d+[.)])\s+", lines[i]):
                item = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", lines[i])
                i += 1
                while i < len(lines) and lines[i].startswith("    ") and not re.match(r"\s*(?:[-*+]|\d+[.)])\s+", lines[i]):
                    item += " " + lines[i].strip()
                    i += 1
                out.append(f"<li>{inline(item)}</li>")
            out.append(f"</{tag}>")
        else:
            para = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"\s*(?:#|\||>|[-*+]\s|\d+[.)]\s)", lines[i]):
                para.append(lines[i].strip())
                i += 1
            out.append("<p>" + inline(" ".join(para)) + "</p>")
    return "\n".join(out)


# ------------------------------------------------------------------ building

def pick(docs: dict[str, list[dict]]) -> dict[tuple[str, str], dict]:
    """One output per (skill, scenario): rep 0."""
    chosen = {}
    for skill, items in docs.items():
        for d in items:
            if d.get("rep", 0) == 0:
                chosen[(skill, d["scenario"])] = d
    return chosen


def prompt_for(skill: str, scenario: str) -> str:
    from box import evals_path
    for entry in json.loads(evals_path(skill).read_text())["evals"]:
        if entry.get("name") == scenario:
            return entry["prompt"]
    return ""


def findings_html(all_docs: list[dict]) -> str:
    parts = []
    for label, phrase in FINDINGS:
        hit = None
        for d in all_docs:
            j = d["output"].lower().find(phrase.lower())
            if j >= 0:
                hit = (d, j)
                break
        if not hit:
            parts.append(f"<li><strong>{html.escape(label)}</strong>: not found in current outputs.</li>")
            continue
        d, j = hit
        excerpt = d["output"][max(0, j - 220): j + 320].replace("\n", " ")
        excerpt = re.sub(r"\*\*|#{2,}\s*|\s{2,}", " ", excerpt).strip()  # excerpts are cut mid-Markdown; show plain text
        where = f"{d['skill'].removeprefix('fdbx-')} / {d['scenario']} / {d['arm'].replace('_', ' ')} / rep {d.get('rep', 0)}"
        parts.append(f"<li><strong>{html.escape(label)}</strong> <span class='where'>{html.escape(where)}</span>"
                     f"<blockquote>…{html.escape(excerpt)}…</blockquote></li>")
    return "<ul class='findings'>" + "\n".join(parts) + "</ul>"


def build(runs: list[str]) -> int:
    base = pick(load("without_skill"))
    skill_docs: dict[str, list[dict]] = {}
    for run in runs:
        skill_docs.update(load("with_skill", run))
    withs = pick(skill_docs)
    pairs = sorted(set(base) & set(withs))
    if not pairs:
        sys.exit("no scenario has both a baseline and a with-skill output")

    rng = random.Random(SEED)
    key, sections, toc = {}, [], []
    for n, (skill, scenario) in enumerate(pairs, start=1):
        pid = f"pair-{n:02d}"
        skill_is_a = rng.random() < 0.5
        a, b = (withs, base) if skill_is_a else (base, withs)
        key[pid] = {"skill": skill, "scenario": scenario, "A": "with_skill" if skill_is_a else "without_skill"}
        title = f"{n}. {skill.removeprefix('fdbx-').replace('-', ' ').title()}: {scenario.replace('-', ' ')}"
        toc.append(f"<li><a href='#{pid}'>{html.escape(title)}</a> <span class='done' data-pair='{pid}'></span></li>")
        qs = []
        for qid, text in QUESTIONS:
            choices = LENGTH_CHOICES if qid == "length" else ["A", "B", "tie"]
            radios = "".join(
                f"<label><input type='radio' name='{pid}-{qid}' value='{c}'> {c}</label>" for c in choices)
            qs.append(f"<div class='q'><span>{html.escape(text)}</span>{radios}</div>")
        wa = len(a[(skill, scenario)]["output"].split())
        wb = len(b[(skill, scenario)]["output"].split())
        sections.append(f"""
<section id='{pid}' class='pair'>
  <h2>{html.escape(title)}</h2>
  <p class='prompt'><strong>Prompt:</strong> {html.escape(prompt_for(skill, scenario))}</p>
  <div class='cols'>
    <article><h3>A <small>{wa} words</small></h3>{md_to_html(a[(skill, scenario)]['output'])}</article>
    <article><h3>B <small>{wb} words</small></h3>{md_to_html(b[(skill, scenario)]['output'])}</article>
  </div>
  <div class='questions'>{''.join(qs)}
    <textarea name='{pid}-notes' placeholder='Notes: what made the difference?'></textarea>
  </div>
</section>""")

    all_docs = [d for items in load("without_skill").values() for d in items] + \
               [d for items in skill_docs.values() for d in items]
    page = PAGE.format(toc="\n".join(toc), sections="\n".join(sections), n=len(pairs),
                       findings=findings_html(all_docs), pairs_json=json.dumps(list(key)))
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    (REVIEW_DIR / "review.html").write_text(page)
    (REVIEW_DIR / "key.json").write_text(json.dumps({"seed": SEED, "runs": runs, "pairs": key}, indent=2))
    print(f"wrote {REVIEW_DIR / 'review.html'} ({len(pairs)} pairs)")
    print(f"wrote {REVIEW_DIR / 'key.json'} (do not open until you have reviewed)")
    return 0


def score(answers_path: str) -> int:
    key = json.loads((REVIEW_DIR / "key.json").read_text())["pairs"]
    answers = json.loads(open(answers_path).read())
    tally: dict[str, Counter] = {qid: Counter() for qid, _ in QUESTIONS}
    by_skill: dict[str, Counter] = {}
    for pid, meta in key.items():
        skill_side = "A" if meta["A"] == "with_skill" else "B"
        for qid, _ in QUESTIONS:
            choice = answers.get(f"{pid}-{qid}")
            if not choice:
                continue
            if qid == "length":
                verdict = {"A too long": "A", "B too long": "B"}.get(choice, choice)
                verdict = "skill too long" if verdict == skill_side else "baseline too long" if verdict in "AB" else verdict
            else:
                verdict = "tie" if choice == "tie" else ("skill" if choice == skill_side else "baseline")
            tally[qid][verdict] += 1
            if qid == "meeting":
                by_skill.setdefault(meta["skill"], Counter())[verdict] += 1
    for qid, text in QUESTIONS:
        print(f"{text}\n   " + ", ".join(f"{k}: {v}" for k, v in tally[qid].most_common()) or "   no answers")
    print("\nMeeting preference by skill:")
    for skill, counts in sorted(by_skill.items()):
        print(f"   {skill.removeprefix('fdbx-'):26s} " + ", ".join(f"{k}: {v}" for k, v in counts.most_common()))
    for pid in key:
        if note := answers.get(f"{pid}-notes"):
            print(f"\n{pid} ({key[pid]['skill'].removeprefix('fdbx-')}, skill was {'A' if key[pid]['A'] == 'with_skill' else 'B'}): {note}")
    return 0


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>fdbx review: baseline vs. with skill</title>
<style>
  body {{ font: 15px/1.5 -apple-system, system-ui, sans-serif; margin: 0; color: #1d1d1f; background: #fafafa; }}
  header, .pair, footer {{ max-width: 1500px; margin: 0 auto; padding: 16px 24px; }}
  header {{ border-bottom: 1px solid #ddd; }}
  h1 {{ font-size: 22px; margin: 8px 0; }}
  .cols {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  @media (max-width: 900px) {{ .cols {{ grid-template-columns: 1fr; }} }}
  article {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 12px 16px; max-height: 75vh; overflow: auto; }}
  article h3 {{ position: sticky; top: -12px; background: #fff; margin: -12px -16px 8px; padding: 10px 16px; border-bottom: 1px solid #eee; }}
  article h3 small {{ color: #888; font-weight: normal; }}
  article h2, article h3:not(:first-child), article h4, article h5, article h6 {{ font-size: 15px; }}
  table {{ border-collapse: collapse; font-size: 13px; margin: 8px 0; }}
  th, td {{ border: 1px solid #ddd; padding: 4px 6px; vertical-align: top; }}
  blockquote {{ border-left: 3px solid #ccc; margin: 8px 0; padding: 2px 10px; color: #444; }}
  .prompt {{ background: #f0f0f3; padding: 8px 12px; border-radius: 6px; }}
  .questions {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 12px 16px; margin-top: 12px; }}
  .q {{ display: flex; flex-wrap: wrap; gap: 14px; align-items: center; margin: 6px 0; }}
  .q span {{ min-width: 380px; font-weight: 600; }}
  textarea {{ width: 100%; min-height: 60px; margin-top: 8px; font: inherit; }}
  .done {{ color: #2a7; font-weight: 600; }}
  .where {{ color: #666; font-size: 13px; }}
  button {{ font: inherit; padding: 8px 14px; border-radius: 6px; border: 1px solid #888; background: #fff; cursor: pointer; }}
  .pair {{ border-bottom: 1px solid #ddd; }}
</style></head>
<body>
<header>
  <h1>fdbx review: which output would you use?</h1>
  <p>Each pair shows two outputs for the same prompt from the same model (DeepSeek V4 Pro). One had the fdbx skill loaded; one only had the method's name. Which is which is shuffled. Read both, answer the five questions, then press <strong>Export answers</strong>. Answers save in this browser as you go.</p>
  <p><strong>Blinding is partial:</strong> with-skill outputs end with an Evidence Ledger and a Handoff, so you may be able to tell them apart. Judge them on the questions anyway: would you use it, did it change how you see the problem, can you trust it, what would you do next, is it worth its length.</p>
  <p>Short on time? Do one pair per method (1, 4, 7, 10), then export. When done, run <code>python3 scripts/make_review_pack.py --score &lt;exported file&gt;</code> to unblind.</p>
  <ol>{toc}</ol>
  <p><button onclick="exportAnswers()">Export answers</button></p>
</header>
{sections}
<footer>
  <h2>Check the probe findings yourself</h2>
  <p>Each claim in <code>docs/baseline-probe-batch-1.md</code> with the passage it comes from:</p>
  {findings}
  <p><button onclick="exportAnswers()">Export answers</button></p>
</footer>
<script>
  const PAIRS = {pairs_json};
  const STORE = "fdbx-review";
  const saved = JSON.parse(localStorage.getItem(STORE) || "{{}}");
  function refreshDone() {{
    for (const pid of PAIRS) {{
      const n = Object.keys(saved).filter(k => k.startsWith(pid + "-") && !k.endsWith("notes")).length;
      document.querySelector(`[data-pair="${{pid}}"]`).textContent = n ? `(${{n}}/5 answered)` : "";
    }}
  }}
  document.querySelectorAll("input[type=radio]").forEach(el => {{
    if (saved[el.name] === el.value) el.checked = true;
    el.addEventListener("change", () => {{ saved[el.name] = el.value; localStorage.setItem(STORE, JSON.stringify(saved)); refreshDone(); }});
  }});
  document.querySelectorAll("textarea").forEach(el => {{
    el.value = saved[el.name] || "";
    el.addEventListener("input", () => {{ saved[el.name] = el.value; localStorage.setItem(STORE, JSON.stringify(saved)); }});
  }});
  function exportAnswers() {{
    const blob = new Blob([JSON.stringify(saved, null, 2)], {{type: "application/json"}});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "fdbx-review-answers.json"; a.click();
  }}
  refreshDone();
</script>
</body></html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", default=[], help="with_skill run id(s); later runs override earlier ones per skill")
    parser.add_argument("--score", metavar="ANSWERS_JSON", help="unblind and tally an exported answers file")
    args = parser.parse_args()
    if args.score:
        return score(args.score)
    return build(args.run)


if __name__ == "__main__":
    sys.exit(main())
