# Baseline probe, batch 2

Batch 2 followed the rule the fdbx plan set for itself: before writing a skill, run the plain model on the method and see where a skill would add anything. Five candidates had sources in the library. Two became skills.

## Baseline

**Run.** 2026-09-24, run `20260924T183759Z`. DeepSeek V4 Pro via OpenRouter, `without_skill` arm: the system prompt only names the method (see `BASELINE_SYSTEM` in `scripts/run_generation.py`). 5 methods × 3 scenarios × 3 reps = **45 outputs, $0.54**, 13 minutes. The scenarios are in each skill's `evals/evals.json`, or in `candidates/` for the three not written.

The checks are regexes in `scripts/probe_baseline.py`, written from the sources before the outputs were read. Two were corrected after reading: the Futures Wheel ring check (the model says "first-/second-/third-order", not Glenn's "primary/secondary/tertiary") and the Horizon Scanning signal-type check (now the toolkit's own list, p. 39).

### What the plain model already does

| Method | Plain model | Gaps a skill could fill |
|---|---|---|
| **Futures Wheel** (Glenn 2009; toolkit pp. 75–78) | Good. Three rings of consequences 6/9, clear cascades, few figures (2/9) | Glenn's Version 2 impact domains 0/9; contradictory consequences side by side 0/9 |
| **Design Fiction** (Bleecker 2009; toolkit pp. 102–107) | Good. Renders the artifact itself 7/9 (for example a printable 2032 brochure), uses "diegetic prototype" 5/9, adds a facilitator's guide, says "not a prediction" | Tension: the artifacts read like marketing, with downsides reduced to a joke |
| **Futures Cone** (Voros 2017) | Mostly. All five classes 6/9, wildcards 8/9 | Preferable as a judgement that can sit in any class 2/9; classes as present-day judgements that change 2/9. One output called it "Causal Layered / Voros Cone"; one invented an "80% confidence area" |
| **Backcasting** (toolkit pp. 91–96; Inayatullah 2008) | Weak. States an end state 8/9, but 3/9 run the timeline forward from today and 3/9 have no dated timeline | Control scoring 0/9; who loses out 0/9; influencing what the team does not control 0/9. Invents the user's own baseline: "60% of buses are low-floor", "30% of bus stops lack accessible boarding" |
| **Horizon Scanning** (toolkit pp. 34–41) | Weak on evidence. PESTLE/STEEP 8/9, but a scoping question 2/9 and a natural agenda 2/9 | 0/9 sources of any kind; trends such as GLP-1 drugs and agent-to-agent commerce stated as present fact. Given the library team's signal "footfall is down but Wi-Fi sessions are up", 2 of 3 outputs added figures the team never gave ("down 12%… up 20%", "up 34%"), and one invented where the signals came from ("frontline observations, partner reports") |

### Decision

Write **Backcasting** and **Horizon Scanning**. Both fail on the thing fdbx exists to fix, invented facts about the present, and both skip the source method's distinctive moves. Set Futures Wheel, Design Fiction and Futures Cone aside: the plain model does most of what a skill would add, and their gaps are small enough to be a paragraph in another skill. Their scenarios are kept in `candidates/`.

This is the rule doing its job. Without the probe, the plan listed all five as batch 2.

## With the skills

### First run

**Run.** `20260924T185658Z`: the two new skills only, 18 outputs, **$0.34**.

The method structure landed: control scoring, who loses out and influence planning each went from 0/9 to 9/9; the scoping question and natural agenda from 2/9 to 9/9. It also found a failure the baseline did not show:

- **Invented links.** One Horizon Scanning output declared *scan* mode, although the runner has no search tool, and listed 14 URLs (McKinsey, Reuters, WHO, SCMP and others), each typed `sourced` in the ledger. An invented link is worse than no link, because it looks checkable.
- **Remembered sources typed `sourced`.** 2/9 Horizon Scanning and 3/9 Backcasting outputs typed model knowledge as `sourced` by naming a report. The same check on batch 1's current outputs found 4/36.

In this probe no claim can honestly be `sourced`: no prompt contains a link and the runner cannot search. So `scripts/probe_baseline.py` now counts any `sourced` row and any URL as a failure.

### Fix 1: "from this session"

Every skill's ledger definition, and `docs/conventions.md`, now says a `sourced` link must come from the user or from a search in this session, and that naming a remembered report does not make it sourced. Horizon Scanning may choose *scan* mode only if a search has actually run, and must say why it chose its mode. `validate_skills.py` enforces the wording.

**Run.** `20260924T190549Z`: all six skills, 54 outputs, **$0.91**. Invented links went from 1/9 to 0/9, and every Horizon Scanning output chose *analyse* or *plan* and said why ("plan — no search tool is available in this session"). But `sourced` rows barely moved: 8/54 outputs. Four only put the method's own sources in the ledger ("CLA was developed by Inayatullah"), which is noise. Four presented remembered facts as `sourced`. The worst was a Four Futures output with 8 such rows ("IRENA, Renewable Power Generation Costs 2023"), and one Horizon Scanning output put a made-up signal ("City X mandates…", "(hypothetical URL)") into its Scans table.

### Fix 2: no URL, not `sourced`

"From this session" was not concrete enough for the model to check against itself. The definition now says the Basis cell of a `sourced` row must hold a URL; no URL, not `sourced`. The ledger is for claims about the world, not the method's own sources, and Horizon Scanning forbids hypothetical signals.

**Run.** `20260924T192125Z`: all six skills, 54 outputs, **$0.82**.

| Outputs (all six skills, 54 each) | Before fixes | Fix 1 | Fix 2 |
|---|---|---|---|
| contain any URL (none can be real here) | 1 | 0 | 1 |
| type any claim `sourced` (none can be here) | 9 | 8 | 2 |

"Before fixes" combines the first batch 2 run with batch 1's current runs (`20260924T115310Z`, `20260924T121528Z`). The two that remain:

- A Futures Triangle output gives a Lloyds Bank URL for a UK digital-skills figure. The rule now demands a URL, and the model supplied one from memory. It may be real, but it did not come from a search. A URL rule moves the failure rather than ending it; only a link checker in a search-enabled run can close it.
- A Horizon Scanning plan shows the scan format with an "(example)" row typed `sourced`. It illustrates the format and is not used as a signal, but it breaks the no-hypothetical-signals rule.

Everything else held on this run. Method checks for all six skills are at or above the batch 1 figures (8–9/9). Ledger rows are correctly typed at 99–100% for five skills. Horizon Scanning shows 89% only because three plan-mode outputs add a placeholder row ("no signals were supplied") with a dash as its type. Backcasting timelines run backwards in 9/9. Horizon Scanning adds no figures to the library team's signals (0/3), chooses *analyse* or *plan* and says why in 9/9, and keeps a Leads to Verify list in 7/9.

## Manual reading

Read per output, for the checks a regex cannot make (runs `20260924T190549Z` and `20260924T192125Z` agree except where noted; `scripts/probe_batch2_manual.py`).

| Check | Baseline | With skill |
|---|---|---|
| Backcasting timeline runs backwards (years descending) | 3/9 | 9/9 |
| Backcasting lists present-day unknowns instead of inventing them | 0/9 | 9/9 |
| Horizon Scanning adds figures to the library team's signals | 2/3 | 0/3 |
| Horizon Scanning keeps unsourced items in a separate Leads to Verify list | 0/9 | 9/9, then 7/9 |
| Horizon Scanning names its mode and why | — | 9/9 |

## What this means

1. **The probe changed the batch.** Three of five planned skills would have added little. That is the most useful result here, and it cost $0.54.
2. **The two new skills fix what the baseline got wrong,** on these checks: the method's own moves appear in 9/9 outputs, the timeline really runs backwards, and invented present-day figures about the user are replaced by a list of unknowns.
3. **A skill can introduce a failure the baseline does not have.** The plain model gave no sources at all. With a skill that asks for sources, one output invented 14. Any skill that asks for evidence needs a probe for fabricated evidence. A concrete rule the model can check (a URL in the cell) worked far better than an abstract one ("from this session"): 2/54 instead of 8/54. But a URL from memory still gets through; only checking links closes that.
4. **Without search, Horizon Scanning is mostly a plan.** In this probe 6/9 outputs are scanning plans with leads to verify, because the runner cannot search. That is the honest output, but the skill's main value, sourced signals, has not been tested. That needs a run with a search tool.

## Limitations

- One model, nine outputs per skill, one probe environment with no search tool.
- The regexes and the manual reading are by the skills' author, not blind.
- The checks measure whether the method's moves and the evidence rules are followed, not whether the outputs are better for a design team. Batch 1's side-by-side review has not been repeated for batch 2.
- The fixes to the `sourced` rule changed batch 1's skills too. Their method checks were re-run with them (above), but batch 1's human review predates the change.

## Next steps

1. A Horizon Scanning run with web search enabled, and a link checker in the probe: every `sourced` URL must resolve and say what the row claims. This also covers the one remembered URL in the last run.
2. Add Backcasting and Horizon Scanning pairs to the review pack (`scripts/make_review_pack.py`) for the independent reviewer planned in batch 1.
3. Revisit the candidates if a design team asks for them. Design Fiction is the likeliest: its gap (tension, not marketing) is small but matters to designers.
