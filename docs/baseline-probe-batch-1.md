# Probe — batch 1: baseline and with-skill

**Question.** When a capable model is told only a method's name, does it make the specific mistakes each fdbx skill was written to prevent? If not, a skill's value has to come from somewhere else.

**Run.** 2026-09-24, run `20260924T112516Z`. DeepSeek V4 Pro via OpenRouter (`deepseek/deepseek-v4-pro`). `without_skill` arm only: the system prompt names the method and asks for a thorough application (see `BASELINE_SYSTEM` in `scripts/run_generation.py`). 4 skills × 3 scenarios × 3 reps = **36 outputs, $0.39**, 12 minutes.

**Reading.** `scripts/probe_baseline.py` counts surface features with regexes. Every regex hit and miss that the conclusions rest on was then checked by reading the output, and several regex results were corrected (noted below). The reader is the author of the skills, and the reading was not blind.

---

## Hypotheses vs. results

| Hypothesis from the design discussion | Result |
|---|---|
| Models stop CLA at the systemic layer | **Rejected.** 9/9 name all four layers and 9/9 reframe the brief. One output identified four worldviews and a builder myth unprompted. |
| Models rank one future "most likely" | **Rejected.** 0/9 use best/worst/most-likely language. |
| Models confuse the futures Three Horizons with McKinsey's growth horizons | **Mostly rejected.** 1/9 clearly McKinsey-flavoured ("run the core vs. build the new"), 1 borderline, 1 regex false positive. A weaker version holds: at least 2/9 turn the horizons into **successive phases** (0–12 months → 3–5+ years), where the source has them co-existing. |
| Models don't know Inayatullah's triangle archetypes | **Confirmed.** 0/9 use the five archetypes. All 9 know pull / push / weight. |
| Models state trends and facts without sources | **Confirmed, strongly.** See below. |

## Per skill

### Causal Layered Analysis (9 outputs)

| Check | Result |
|---|---|
| Names all four layers | 9/9 |
| Reframes the brief | 9/9 |
| Says who acts at each layer | 0/9 cover all four layers; most cover 0–2 |
| Proposes an alternative metaphor | 3/9 |
| Writes scenarios (Inayatullah: they differ in kind per layer) | 1/9 |

The plain model knows the method. What it leaves out is the structure Inayatullah uses to turn the analysis into action: who acts at each layer, an alternative metaphor, and scenarios by layer.

### Four Futures (9 outputs)

| Check | Result |
|---|---|
| All four Dator types, with his names | 9/9 (the regex reported 8/9: one output labels the type "Growth") |
| Ranks a future best / worst / most likely | 0/9 |
| Uses "Steady state" as the type name | 0/9 (the regex hit was "steady-state economy" describing the Discipline future) |
| Collapse framed positively | 7/9 by future name ("Resilient Localism", "The Resilient Ledger"); 2/9 named as disasters ("Grid Fragility – Energy Scarcity", "The Fractured Academy") |
| Dator's questions D/E (five things to do now) | 0/9 |
| An artifact from the future | 2/9 |

The plain model knows Dator's typology well. It does not run Dator's *exercise*: experiencing each future through the A–E questions and five actions each way.

### Three Horizons (9 outputs)

| Check | Result |
|---|---|
| Futures version (H1 declining, H3 emerging, H2 transition) | Majority, by reading |
| McKinsey growth framing | 1/9 clear, 1 borderline, 1 false positive |
| Horizons as successive time phases | ≥2/9 |
| Explicit H2+ / H2− | 1/9; about 3/9 make a sustaining-vs-transformative distinction in their own words |
| Pockets of the future | ~2/9 name the idea |
| **Invented "pocket of the future" presented as real** | 1 confirmed: "The Millfield Pilot", with invented figures ("uptake rose 25%", "cost is currently 35% higher") |

### Futures Triangle (9 outputs)

| Check | Result |
|---|---|
| Pull / push / weight structure | 9/9 |
| Uses Inayatullah's five archetypes | 0/9 |
| Weights given per image (Inayatullah: "each image has differing weights") | 0/9: all nine have one shared "weight of the past" section |
| Asks which future the strategy serves (used future) | 1/9 |

## Cross-cutting: unsourced facts

Across all 36 outputs, 37 lines contain a percentage or money figure. **4 are hedged or sourced.** Many figures belong inside an imagined future, which is fine. At least 9 are **present-day facts stated as true with no source**, for example:

- "Branch foot traffic dropping 10–15% year-over-year"
- "70%+ of routine transactions have already migrated to self-service"
- "30–40% of white-collar workers telecommute 2–3 days/week"

Two invent facts about the user's own situation, where the prompt gave no data: "uptake has dropped by 8% in three years" and "childhood obesity in the city is 2% above national average". **0/36** outputs label any claim as sourced, user-supplied or assumed. (The regex reported 2/9 for Three Horizons; both were "Underlying Assumption" table columns, not evidence labels.)

## What this means for fdbx

1. **Method knowledge is not where the skills add value** for this model. It already knows CLA's layers, Dator's four futures, the pull/push/weight triangle and the futures Three Horizons. Long explanations of *what* a method is may be padding. edbx's RESULTS.md found that padding sections diluted actionability.
2. **The Evidence Ledger is the best-supported addition.** Unsourced present-day facts, invented facts about the user's context, and an invented "existing" initiative are exactly what it is designed to catch.
3. **The method-fidelity details the plain model skips are the next most likely sources of value:** who acts per layer and alternative metaphors (CLA); Dator's A–E questions, five actions and artifacts (Four Futures); per-image weights and archetypes (Triangle); H2+/− and horizons co-existing rather than succeeding each other (Three Horizons). Whether these make outputs *better*, and not just more faithful, is not shown by this probe.
4. **Two guardrails to strengthen:** Three Horizons should name "successive phases" as an error alongside the McKinsey framing; its pockets-of-the-future rule should say explicitly that an invented example with figures is the failure it targets.

## Limitations

- One model. Claude, GPT or Gemini may fail differently.
- Nine outputs per skill. These are counts, not significance tests.
- Regexes miss wording they were not written for (several corrections above). The manual reading was done by the skills' author, not blind.
- The probe measures what the plain model does, not whether the skills do better. That needs the with-skill arm.

## With-skill comparison

**Run.** Run `20260924T115310Z`: the same 36 tasks with each SKILL.md as the system prompt. **$0.76**, 16 minutes. Compare with `python3 scripts/probe_baseline.py --arm compare`.

Several regex results were wrong on first reading and were corrected by reading the outputs:

- **Handoff** appeared absent (0/9) because the pattern's `^` only matched the start of the text. Fixed with `(?m)`.
- **"Most likely" and McKinsey hits** jumped in the with-skill arm because outputs repeat the skill's own rule back ("No future is labelled best, worst, or most likely"). Negated lines are now excluded.
- **Manager / entrepreneur / visionary** scored 0/9 because the skill's output uses a horizon-perspectives table, not those words. Checked directly instead.

| Skill | Check | Baseline | With skill |
|---|---|---|---|
| CLA | who acts / problem-solver per layer | 0/9 | 8/9 |
| CLA | alternative metaphor | 3/9 | 9/9 |
| CLA | scenarios | 1/9 | 9/9 |
| Four Futures | ranks a future (after excluding echoed rules) | 0/9 | 0/9 |
| Four Futures | Dator's five things to do now | 0/9 | 9/9 |
| Four Futures | artifact from the future | 2/9 | 9/9 |
| Triangle | Inayatullah archetypes | 0/9 | 9/9 |
| Triangle | weights per image | 0/9 | 9/9 |
| Triangle | used / disowned future | 1/9 | 9/9 |
| Three Horizons | H2+ / H2− | 1/9 | 9/9 |
| Three Horizons | pockets of the future | ~2/9 | 9/9 |
| Three Horizons | horizon perspectives section | 0/9 | 9/9 |
| Three Horizons | McKinsey framing (after excluding echoed rules) | 2/9 | 1/9 |
| All | Evidence Ledger present | 0/36 | 36/36 |
| All | Ledger rows correctly typed (user-supplied / sourced / assumption) | — | **108 of 268 rows (40%)**: Triangle 97%, CLA 41%, Three Horizons 32%, Four Futures 0% |
| All | Outputs whose ledger is fully typed | 0/36 | 9/36 (Triangle 7, CLA 1, Three Horizons 1, Four Futures 0) |
| All | Handoff | 0/36 | 36/36 |

Median words: CLA 1461 → 1376; Triangle 2054 → 1818; Three Horizons 1678 → 1856; **Four Futures 2197 → 3671 (+67%)**.

### What the comparison shows

1. **The skills reliably add the method structure the plain model skips.** Every "required" feature goes from rare to 8/9 or 9/9. This shows the skills are *followed*. It does not show the outputs are *better*; that needs a quality judgement this probe does not make.
2. **Invented pockets of the future are replaced by real, named programmes** in the school-meals Three Horizons outputs (Brazil's PNAE, the Soil Association's Food for Life, Ghent's Thursday Veggie Day, New York's universal free lunch). Their details have not been fact-checked.
3. **A skill defect: the ledger's evidence types.** Only the Futures Triangle outputs used the three types consistently (97% of rows). The others invented their own: "Trend / Emerging issue" (Four Futures, 9/9), "Empirical / Reference / General knowledge / Pocket example" (Three Horizons), "Public narrative / Scientific evidence" (CLA). The Futures Triangle was the only SKILL.md that named the three types. The others said "with their type", which the model reasonably read as "what kind of trend". **Fixed:** the vocabulary is now in each skill's Output Format, the ambiguous wording is gone, and `validate_skills.py` fails any skill that does not name all three types. The rule flagged exactly the three skills whose outputs failed.
4. **Figures still appear outside the ledger.** Most are inside imagined futures, which is expected. Some present-day statistics in the Three Horizons H1 sections still appear with no ledger row ("print circulation declines 6–10% year-on-year").
5. **Four Futures is 67% longer.** The extra length comes from Dator's structure: A–E for each future, including 5 + 5 actions for each of four futures, plus four artifacts. Whether that length earns its keep is the open question edbx's RESULTS.md raised about padding.

## Re-run after the ledger fix

**Run.** Run `20260924T121528Z`: CLA, Four Futures and Three Horizons with the fixed SKILL.md (27 generations, **$0.59**). The Futures Triangle was not changed and serves as the control. Compare with:

```bash
python3 scripts/probe_baseline.py --arm compare --run 20260924T115310Z --run 20260924T121528Z
```

The first pass of the row-level metric undercounted: the model writes the right types with backticks (`` `assumption` ``) or a non-breaking hyphen ("user‑supplied"). The matcher now accepts those variants. Re-scored with the same matcher, the pre-fix numbers do not change, so the tolerance does not inflate anything.

| Skill | Ledger rows correctly typed, before fix → after | Outputs fully typed |
|---|---|---|
| Four Futures | 0/87 (0%) → **87/87 (100%)** | 0/9 → 9/9 |
| CLA | 22/54 (41%) → **64/65 (98%)** | 1/9 → 8/9 |
| Three Horizons | 18/57 (32%) → **65/65 (100%)** | 1/9 → 9/9 |
| Futures Triangle (unchanged) | 68/70 (97%) | 7/9 |

The one remaining off-vocabulary cell is a valid type with a note ("user‑supplied (implicit in the brief)"). Four Futures ranking stays at 0/9: the only new hit was "None is a prediction, a best case, or a worst case", a negation the filter now recognises.

**The fix labels invented claims; it does not remove them.** The ledgers are now honest ("School‑meal uptake is around 60% and falling | assumption | not confirmed for this city"; "Local school with 80% plant‑based menu exists | assumption | Hypothetical but plausible; user would need to validate"). But the body can still contradict its own ledger: one action item says "Visit the school that already runs a 80% plant‑based menu", presenting as real a school the ledger calls hypothetical. A reader who checks the ledger is protected; a reader who skims the body is not.

## Human review (reviewer 1)

**Setup.** `scripts/make_review_pack.py` paired one baseline and one with-skill output per scenario (rep 0; with-skill outputs from the fixed skills), shuffled A/B with a fixed seed, and asked five questions per pair. Reviewer 1 is the fdbx owner. All 12 pairs answered, no notes written. Answers are kept locally in `eval-framework/review/answers-2026-09-24-reviewer-1.json`.

| Question | With skill | Baseline | Tie |
|---|---|---|---|
| Which would you rather bring into a design meeting? | **12** | 0 | 0 |
| Which made you see the problem differently? | **11** | 0 | 1 |
| Which is easier to trust? Can you tell fact from assumption? | **11** | 0 | 1 |
| Which gives you clearer next steps? | **11** | 0 | 1 |
| Is either longer than what it gives you? | neither: 11, both: 1 | | |

Each skill won 3/3 on "bring into a meeting". The ties were CLA remote-team (insight), Three Horizons retail bank (trust) and Three Horizons school meals (next steps). The only length complaint was Three Horizons school meals ("both too long"). No Four Futures pair was judged too long, despite the with-skill outputs being ~50% longer.

**How far this goes.** 12/12 is unlikely by chance if the reviewer had no preference (two-sided sign test p ≈ 0.0005). But chance is not the main risk:

- **Partial blinding.** With-skill outputs end with an Evidence Ledger and a Handoff, so the reviewer could often tell which side was which, and the reviewer commissioned the skills. Expectation can produce a clean sweep.
- **One reviewer, one model, one rep per scenario.**
- No notes, so we do not yet know *what* made the difference: the method structure, the ledger, or the format.

## Next step

1. **A second, independent reviewer**: a designer who has not seen fdbx, using the same page.
2. **A stricter blind**: rebuild the pack with the Evidence Ledger and Handoff stripped from the with-skill outputs, so only the body is compared. If preference holds, the method structure is doing the work. If it collapses, the ledger and format are.
3. Decide whether "labelled" is enough, or whether the skills should also require the body to hedge anything the ledger marks as an assumption (for example "if a school locally runs…"). The second is stricter and may make outputs harder to read.
4. Write `conformance.json` rubrics and calibrate them with Jev, so pass rates come from code and a calibrated judge, not from regexes read by the skills' author.
5. Judge quality at scale: blind pairwise comparison by a model that is not DeepSeek or Claude, alongside the human reviews.

## Previously planned next step (done)

Re-run the with-skill arm for the three skills whose SKILL.md changed (CLA, Four Futures, Three Horizons: 27 generations, about $0.60 actual, ~$2.50 padded) to confirm the ledger fix. Then write `conformance.json` rubrics and calibrate them, so pass rates come from code and calibrated Jev rather than regexes read by the author.
