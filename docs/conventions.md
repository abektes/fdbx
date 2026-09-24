# fdbx conventions

Every fdbx skill follows edbx's house style (Overview, Use This Skill When,
Inputs, Workflow, Output Format, Guardrails, Deliverable Quality Bar) and adds
four conventions. `scripts/validate_skills.py` enforces the first three;
`scripts/check_provenance.py` enforces the fourth.

## 1. Evidence Ledger (in every output)

Futures work runs on claims about the present: trends, signals, statistics,
who holds which view. A model will state these fluently whether or not they
are true. The ledger makes the basis of each one visible.

```markdown
### Evidence Ledger

| Claim used as input | Type | Basis |
|---|---|---|
| Remote work share has plateaued since 2023 | assumption | Model knowledge; verify before use |
| Our churn rose 4 points after the price change | user-supplied | Stated in the brief |
| EU AI Act obligations for general-purpose models apply from Aug 2025 | sourced | [link] |
```

- **Type** is one of `user-supplied`, `sourced` (with a link the user can open) or `assumption`.
- Anything the model knows only from training is an `assumption`, however confident it sounds.
- A trend, driver, statistic or "pocket of the future" never appears in the output without a ledger row.

## 2. Handoff (in every output)

Futures methods are strongest in sequence, and many end where an edbx method
should begin. The handoff makes the next step explicit.

```markdown
### Handoff

**Assumptions surfaced:** the beliefs the brief was resting on, one per bullet.
**Open decisions:** what the team now has to choose, and by when if known.
**Suggested next method:** one fdbx or edbx skill, and why this output feeds it.
```

## 3. Adaptation labelling (in every SKILL.md)

A skill has two kinds of content: what the source describes, and what fdbx
adds to fit design work. They must never blur. Anything the source does not
describe is marked:

```markdown
> **fdbx adaptation:** reading the design brief as the litany is ours, not
> Inayatullah's. The method works on any issue; we point it at the brief.
```

Sourced content is written in our own words and cited in `## Sources` and in
`references/provenance.md`. Do not copy passages from sources.

## 4. Provenance table (references/provenance.md)

One row per claim the skill attributes to a source:

```markdown
| # | Skill element | Source | Locator | Anchor phrase | Note |
|---|---|---|---|---|---|
| 1 | Four layers of CLA | `inayatullah-1998-cla` | § Abstract | litany, social causes, discourse/worldview and myth/metaphor | |
| 2 | No best or worst case | `dator-2009-manoa` | p. 7 | no such thing as either a best case | |
```

- **Source** is a key in `sources/manifest.json`.
- **Locator** is `p. N` (printed page; the manifest's `page_offset` maps it to the PDF page) or `§ Heading` for HTML sources without page numbers.
- **Anchor phrase** is 3–12 words from that page. It is a pointer so a reader can find the passage, not a quotation to reuse.
- **Note** records anything a reader should know, e.g. "Inayatullah calls this Steady state (2008, p. 16)".

The check ignores case, punctuation and line breaks, and reports the real page
if an anchor is found somewhere other than where it is cited.
