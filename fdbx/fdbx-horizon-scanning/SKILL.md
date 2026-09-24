---
name: fdbx-horizon-scanning
description: Use when a team needs to know what is changing around a product, service or policy area — run horizon scanning as set out in the UK Government Office for Science Futures Toolkit — a scoping question, signals of change gathered from sources the user supplies or a live search finds (never from model memory), tagged by PESTLE and type, clustered into a natural agenda, rated for impact, likelihood and newness, and written up as the drivers worth acting on. Trigger for "horizon scan", "horizon scanning", "signals of change", "weak signals", "what should we be watching", "trend scan", "environmental scan", "STEEP / PESTLE scan", "what do these signals add up to", or when a futures method needs real inputs about the present.
version: "0.1"
tags: [futures, evidence]
---

# Horizon Scanning

## Overview

Horizon scanning is the systematic collection of insights on emerging trends and weak signals of change, to identify potential threats, risks and opportunities. This is the definition in the UK Government Office for Science (GO-Science) *Futures Toolkit*, the source for this skill. A scan is a set of **scans**: short, sourced records of an external development, each noting what it is, how it relates to the question, and why it matters.

The toolkit's version has five steps: recruit scanners, identify sources, gather scans in a consistent format, analyse them, and write up. Three features separate it from a list of trends:

- **A scoping question comes first.** Scanning is immersive, and it is easy to go down rabbit holes. The question decides what counts as a signal.
- **Every scan carries its source.** The toolkit asks scanners to go back to the original source material and to include links.
- **Breadth is checked, not assumed.** Count scans per PESTLE category so the scan doesn't drift into, for example, only technology. Then group them by the themes that emerge from the scans themselves, which the toolkit calls a **natural agenda**.

> **fdbx adaptation — where signals come from.** A model cannot scan the world from memory. What it "knows" is a snapshot, unsourced, and fluent enough to pass for evidence. The plain model shows this: asked for a scan, it lists trends as present-day fact with no sources, and it adds figures to signals the user supplied ("footfall down 12%") that the user never gave. So this skill takes signals from only three places, and says which one each came from:
>
> 1. **user-supplied**: signals the user or their scanners collected
> 2. **sourced**: found in this session by a web search or a document the user shared, with a link the reader can open
> 3. **lead to verify**: something the model believes may be happening. It is shown in a separate list, typed `assumption`, never counted as a signal, and never given a figure
>
> The toolkit notes that AI systems can help by gathering basic information for people to structure. This skill takes that role and leaves the judgement to the team.

## Use This Skill When

- The team wants to know what is changing around its product, service or area before setting strategy.
- Staff have collected signals and the team wants to know what they add up to.
- Another fdbx method needs real inputs: pushes for `fdbx-futures-triangle`, pockets of the future for `fdbx-three-horizons`, present conditions for `fdbx-four-futures`, or events outside the team's control in `fdbx-backcasting`.
- You want to set up a scanning routine rather than a one-off report.

## Inputs

- **The scoping question** or the topic, with a time horizon. If the user gives only a topic, Step 1 drafts a question.
- **Signals**, if the user has any: notes, links, clippings, observations from staff.
- **Search access**: whether you can actually run a web search in this session. Having heard of a report is not search access.
- **Mode:**
  - *analyse*: the user supplies signals; the skill structures and interprets them
  - *scan*: the skill searches for signals, with links, then analyses them. Choose it only if you have run a web search in this conversation and can see its results
  - *plan*: no signals and no search; the skill writes the scoping question, a source list, a scan format and leads to verify, so the team can scan

State the mode and why at the top of the output. If you have no search tool, you are in *analyse* or *plan* mode, whatever the user asked for, and you say so.

## Workflow

### Step 1 — Scoping question

Write one question the scan serves, with a horizon and the organisation's point of view, for example: "What changes in the next ten years could alter how households get groceries, and what would they mean for our delivery app?" Everything that follows is judged against it.

### Step 2 — Sources

Name where to look, beyond the organisation's usual sources: the toolkit's aim is to find where you need to know more. Its list:

- other published scans and trend collections (a "scan of scans")
- directed research on the web and in academic literature
- experts and people with an outside view
- professional and industry journals
- headlines from around the world
- blogs and social media of leading commentators and researchers, where issues show up before they reach the mainstream
- sources in languages other than English

In *scan* mode, run the searches and record what you find. In *plan* mode, turn this into a list the team can use.

### Step 3 — Scans, in one format

Record every signal as a scan with the toolkit's metadata:

| Field | Content |
|---|---|
| Signal | What the scan is about, in one sentence |
| Source | Link or the user's note. Go back to the original source, not a summary of it |
| Date | When it was published or observed |
| Evidence type | `user-supplied` or `sourced` |
| PESTLE | Political, economic, societal, technological, legislative or environmental |
| Relevance | How it relates to the scoping question |
| Why it matters | What the scanner thinks it could lead to |
| Timescale and importance | An initial judgement |

Do not add figures, names or dates to a user-supplied signal that the user did not give. If a number would help, write the question to ask instead.

Then **count scans per PESTLE category.** If one category dominates or one is empty, say so and, in *scan* mode, search the empty one.

### Step 4 — Analyse

1. **Type each signal** using the toolkit's list: established trend, expected development, newly emerging issue, new risk or opportunity, or possible future event.
2. **Cluster into a natural agenda**: group the scans by the themes that emerge from them, not by PESTLE. Name each theme.
3. **Rate impact and likelihood** (1–5 each) and place each theme on the matrix. The toolkit marks the high-risk quadrant as vital for planning and the most important to report, and asks you to cover low-probability, high-impact drivers as well.
4. **Rate newness to the organisation.** Is it already well understood? By everyone? Do current strategies already account for it?
5. **Select four to eight drivers of change** to take forward.

Include signals that seem irrelevant at first. The toolkit tells scanners to err on the side of including them.

### Step 5 — Write up

Summarise in a form the team can act on:

- the new drivers of change that warrant action, with recommendations
- changes with high potential impact that need more research
- established trends, for completeness
- what to watch next: the questions and sources for the next round of scanning

If scanning continues, use this round's output to focus the next.

### Leads to verify

> **fdbx adaptation.**

List anything the model believes may be relevant but has not sourced in this session. One line each, phrased as something to check ("Check whether…"), typed `assumption` in the Evidence Ledger. Do not include leads in counts, clusters, ratings or drivers.

## Output Format

A blank version is in `assets/horizon-scan-template.md`.

### Horizon Scan: [Topic], to [Year]

**Scoping question:** …
**Mode:** analyse / scan / plan, and why
**Signals from:** user-supplied (n), sourced (n)

### Scans

| # | Signal | Source | Date | Type of evidence | PESTLE | Why it matters |
|---|---|---|---|---|---|---|

**Balance:** scans per PESTLE category, and any gap.

### Natural Agenda

For each theme: its name, the scans in it (by #), and what the theme could mean for the subject.

### Signal Types

| Theme or scan | Established trend / expected development / emerging issue / risk or opportunity / possible event |
|---|---|

### Impact and Likelihood

| Theme | Impact (1–5) | Likelihood (1–5) | Quadrant | Newness to the organisation |
|---|---|---|---|---|

### Drivers of Change to Take Forward

Four to eight, each with its recommendation or research need.

### What to Watch Next

Questions and sources for the next round.

### Leads to Verify

Unsourced items to check. Not part of the analysis above.

### Evidence Ledger

Type is one of `user-supplied` (stated in the brief or by the user), `sourced` (the Basis cell holds a URL the reader can open, which came from the user or from a search or tool result in this session; no URL, not `sourced`), or `assumption`. Anything that comes from model knowledge is an `assumption`, however confident it sounds, even when you can name the report or organisation it comes from. The ledger records claims about the world used as input, not this method's own sources. Do not use other types such as "trend" or "general knowledge".

| Claim used as input | Type | Basis |
|---|---|---|

### Handoff

**Assumptions surfaced:** …
**Open decisions:** …
**Suggested next method:** …

## Guardrails

- A signal is `user-supplied` or `sourced`. Nothing from model memory enters the Scans table, the clusters, the ratings or the drivers. It goes under Leads to Verify.
- No hypothetical or illustrative signals ("City X mandates…"). A signal is something that happened or was observed, with its source.
- Never write a URL, report title, publisher or publication date that did not come from the user or from a tool result in this session. A source you remember is a lead to verify, not a source. An invented link is worse than no link: it looks checkable.
- Never add a figure, a name, a date or a source to a user's signal. "Footfall is down" stays "footfall is down".
- Never describe a sourcing process that did not happen ("signals were drawn from patents, surveys and expert interviews"). Say exactly where each signal came from.
- A `sourced` signal needs a link the reader can open. If a search result cannot be opened or does not say what you need, do not use it.
- Start from the scoping question. A scan without one is a list of trends.
- Count PESTLE coverage and report gaps; do not let one category, usually technology, stand in for the whole environment.
- Ratings are the team's starting judgement, not findings. Say so.
- Do not present the scan as a prediction.

## Deliverable Quality Bar

A strong Horizon Scanning output:

- starts from a scoping question with a horizon
- records every signal as a scan with its source, date, evidence type, PESTLE category and why it matters
- uses only `user-supplied` or `sourced` signals in the analysis, and puts anything else under Leads to Verify
- adds no figures or details to user-supplied signals
- reports PESTLE balance and any gap
- clusters the scans into a natural agenda of named themes
- types signals (established trend, expected development, emerging issue, risk or opportunity, possible event)
- rates themes for impact, likelihood and newness to the organisation
- selects four to eight drivers of change, with recommendations or research needs
- ends with a Handoff naming the next method and why

## Integration with Other Skills

- **fdbx-futures-triangle** — the drivers become its pushes, now with sources.
- **fdbx-three-horizons** — sourced signals are candidates for pockets of the future.
- **fdbx-four-futures** — the scan is the present-day grounding for Step 1.
- **fdbx-backcasting** — scan for the critical events outside the team's control.
- **fdbx-causal-layered-analysis** — take the strongest theme and read it at four depths.
- **edbx-stf-et** and **edbx-worrystorming** — take a high-impact driver and ask whom it could harm.

## Sources

- UK Government Office for Science (2024). *The Futures Toolkit*, 2nd edition, pp. 34–41 and 113–114. The definition, the five steps, sources, the scan format and metadata, the tips, the signal types, the natural agenda, the impact and likelihood matrix, newness, drivers, and the write-up. (`go-science-2024-toolkit`)

Every claim above is tied to a page in `references/provenance.md`.

## See Also

- `references/scanning-routine.md` — setting up scanning as a team routine
- `references/provenance.md` — where each element of this skill comes from
