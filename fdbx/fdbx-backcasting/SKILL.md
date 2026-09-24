---
name: fdbx-backcasting
description: Use when a team has a preferred future or a hard goal (a target year, a commitment, a vision) and needs the path back to today — apply backcasting as set out in the UK Government Office for Science Futures Toolkit, with Elise Boulding's "remember the future" move from Inayatullah — to work backwards from the end state, find the critical events, score each as wholly, partly or not in our control, name who gains and who loses, and turn it into an action plan. Trigger for "backcasting", "backcast", "work backwards from", "how do we get to 2035", "roadmap to a goal", "net zero by", "we have a vision but no plan", "present bias", or when a four-futures or three-horizons output needs a path to now.
version: "0.1"
tags: [futures, action]
---

# Backcasting

## Overview

Backcasting connects a chosen future to the present. You stand in the preferred future and ask what had to happen to get there, then what had to happen before that, all the way back to today. The UK Government Office for Science (GO-Science) *Futures Toolkit* describes it as a way to overcome **present bias**, the desire for immediate gains over long-term ones.

Working backwards changes what a plan contains:

- **Every step, not just the goal.** A forecast from today stops where the current trends run out. A backcast has to fill every gap between the end state and now, so the plan has to be complete.
- **What is not ours to control.** The toolkit scores each critical event as wholly, partly or wholly out of your control. Events outside your control stay on the timeline. You plan how to influence them.
- **Who loses out.** For each event the toolkit asks who benefits and who loses, and who may *feel* they are going to lose, even if they won't.

Inayatullah (2008) traces the technique to Elise Boulding. She moved people into the preferred future and asked for their *memories* of the years that led there. He adds that the same move works on a feared future: backcast the worst case to find the steps that lead to it, then block them.

> **fdbx adaptation:** we point backcasting at design and product decisions. The end state is described as what people are able to do, not only as metrics. And the present-day baseline must come from the user. The plain model invents the team's current figures ("60% of buses are low-floor"); this skill asks for them instead and records any it does not have as unknown.

## Use This Skill When

- The team has a target with a year on it (reusable packaging by 2040, a fully accessible network by 2035) and a roadmap that runs out long before it.
- A preferred future came out of `fdbx-four-futures` or a visioning exercise and nobody has worked out the path.
- The plan only contains what the team controls, and everything else is labelled a "dependency".
- You want to test whether a goal is achievable at all before committing to it.
- You want to see how a feared future could arrive, in order to prevent it.

## Inputs

- **The preferred future or goal**, with a year. If the user has only a slogan, Step 1 turns it into an end state.
- **Where things stand now.** Current state, constraints and any figures the user has. Do not fill gaps with invented numbers; mark them unknown and list them as questions.
- **Who is involved**: the team running the exercise and the other actors whose decisions matter.
- **Mode:** *preferred* (the default: backcast toward a future you want) or *avoid* (backcast a feared future to find the steps that lead to it).
- Optional: *workshop kit*. See `references/workshop-guide.md`.

## Workflow

### Step 1 — Introduce the preferred future

State the end state in the target year. The toolkit takes it from a scenarios or visioning exercise. If the user gives only a goal, write the end state as:

- **What people can do** in that future that they cannot do now.
- **Conditions that are true**: the few things an observer could check.
- **What is no longer true**: practices, products or rules that have gone.

> **fdbx adaptation:** "what people can do" is ours. It keeps the end state about the people a design serves, not only about targets.

### Step 2 — Key differences between now and then

Compare the present and the preferred future on three questions from the toolkit:

- Where are we now, and where are we in the preferred future?
- What drives change now, and what will drive it then?
- What is the delivery environment like now, and then?

Use PESTLE (political, economic, societal, technological, legislative, environmental) to make sure no category is skipped. Any statement about the present goes in the Evidence Ledger, typed `user-supplied`, `sourced` or `assumption`.

### Step 3 — Build the timeline backwards

Start at the target year. Ask: *what needed to happen for this to be true?* Then, for that event: *what had to happen before that to enable it?* Repeat until you reach the present. Write the timeline from the future toward now, not the other way round.

For the first pass, use Boulding's move (via Inayatullah): speak from inside the future. "It is 2040. Looking back, the turning point was…" The memories become events on the timeline.

Then mark the **critical events**: the ones that must occur if the preferred future is to happen.

### Step 4 — Score control

Score every critical event:

1. wholly in our control
2. partly in our control
3. wholly out of our control

Keep the events scored 3. The toolkit warns that many factors may prove to be outside your control and says to include them anyway, so the picture is complete.

### Step 5 — Events in our control (scored 1 or 2)

For each, record:

- the impact on delivering the preferred future
- who benefits and who loses out
- how certain it is that the event will happen
- the enablers that make it easier
- the barriers to overcome
- the key steps to take now

### Step 6 — Events outside our control (scored 3)

For each, record:

- who has control
- the impact if the event does not happen
- what we can influence to make it more likely, and the steps that would take
- what benefits or loses out (people, but also the environment or other systems)
- who will lose out, or may feel they are going to

### Step 7 — Action plan

Summarise the steps into an action plan: what to start now, what comes next, and which decisions have to be made by when. Name an owner for each action. Mark the **decision points**: the dates by which a critical event must have happened for the path to stay open.

Inayatullah notes that the steps can be run as a budgeted plan or as action learning, where small experiments start to create the future. Say which one this plan is.

### Forward check (optional, from the toolkit's quick version)

Build a second timeline *forward* from today toward the preferred future, without looking at the backcast. Compare the two, then blend them into one: the toolkit says this identifies the key decision points.

> **fdbx adaptation:** the toolkit runs this with two workshop groups. We let one analyst do both. Where the timelines diverge, check the forward one for present bias: steps assumed to happen only because they are already underway.

### Avoid mode

Backcast a feared future the same way. The critical events become the ones to block, and the action plan lists what to do so that they do not happen. Steps 4–6 still apply.

## Output Format

A blank version is in `assets/backcasting-template.md`.

### Backcasting: [Subject], [Year]

One paragraph: the goal, the mode (preferred or avoid), and who is backcasting.

### The Preferred Future in [Year]

**What people can do:** …
**Conditions that are true:** …
**What is no longer true:** …

### Key Differences, Now and Then

| Area (PESTLE) | Now | In [Year] | Driver of the change |
|---|---|---|---|

### Memories from [Year]

Three to five short first-person memories from people inside the future: "It is [Year]. Looking back, the turning point was…"

### Backward Timeline

Read from the top: each row is what had to happen before the row above it.

| When | Event or condition | What had to happen before this | Critical? | Control (1/2/3) |
|---|---|---|---|---|
| [Year] | Preferred future | | | |
| … | | | | |
| Now | | | | |

### Critical Events in Our Control

| Event | Control | Impact on the future | Who benefits / who loses out | Certainty | Enablers | Barriers | Steps now |
|---|---|---|---|---|---|---|---|

### Critical Events Outside Our Control

| Event | Who has control | If it does not happen | What we can influence, and how | Who loses out, or may feel they will |
|---|---|---|---|---|

### Forward Check

*(optional)* Where the forward timeline diverges from the backcast, and the decision points where they meet.

### Action Plan

| Action | Owner | Start | Decision point it serves |
|---|---|---|---|

Plan type: budgeted plan or action learning.

### Unknowns to Fill

Present-day facts the backcast depends on that the user did not supply. One question per unknown.

### Evidence Ledger

Type is one of `user-supplied` (stated in the brief or by the user), `sourced` (the Basis cell holds a URL the reader can open, which came from the user or from a search or tool result in this session; no URL, not `sourced`), or `assumption`. Anything that comes from model knowledge is an `assumption`, however confident it sounds, even when you can name the report or organisation it comes from. The ledger records claims about the world used as input, not this method's own sources. Do not use other types such as "trend" or "general knowledge".

| Claim used as input | Type | Basis |
|---|---|---|

### Handoff

**Assumptions surfaced:** …
**Open decisions:** …
**Suggested next method:** …

## Guardrails

- Work backwards. Every row of the timeline must be something that had to happen *before* the row above it. A forward roadmap presented in reverse order is not a backcast.
- Only type a claim `sourced` if its link came from the user or from a search in this session. A regulation or report you remember is an `assumption`, even if you can name it.
- Never invent the user's present-day figures (their share, their rates, their budgets). If the backcast needs a number the user did not give, write "unknown", add it to Unknowns to Fill, and continue.
- Keep events outside the team's control on the timeline. Do not turn them into a footnote about "dependencies".
- Name who loses out from each critical event, including people who only feel they will lose out. A plan where nobody loses has not been examined.
- The end state must be specific enough to backcast from. "Be the most accessible network" is not; "any passenger can travel from street to seat without assistance, on every line" is.
- A backcast is not a forecast. Do not say the future *will* be reached; say what must happen for it to be.
- Trends, drivers and present-day facts go in the Evidence Ledger with their evidence type (`user-supplied`, `sourced`, or `assumption`).

## Deliverable Quality Bar

A strong Backcasting output:

- describes the preferred future: what people can do, the conditions that are true, and what is no longer true
- compares now and then across PESTLE areas, with present-day claims in the Evidence Ledger
- builds the timeline backwards, each step asking what had to happen before it
- marks the critical events and scores each 1, 2 or 3 for control
- names who benefits and who loses out for the critical events in the team's control
- says, for each event outside the team's control, who has control and what the team can influence
- ends in an action plan with owners and decision points, and says whether it is a plan or action learning
- lists present-day facts the user did not supply as unknowns rather than inventing them
- ends with a Handoff naming the next method and why

## Integration with Other Skills

- **fdbx-four-futures** — its preferred-future sketch is the natural input to Step 1. A Collapse future can be backcast in avoid mode.
- **fdbx-three-horizons** — backcast from the third horizon; the critical events in the team's control are candidate H2+ innovations.
- **fdbx-horizon-scanning** — scan for signals that the critical events outside the team's control are, or are not, happening.
- **fdbx-causal-layered-analysis** — if the preferred future is only a target at the litany level, run CLA first to find the worldview it depends on.
- **edbx-pledge-works** and **edbx-ethical-contract** — turn the action plan into commitments someone is accountable for.
- **edbx-worrystorming** — run on the action plan, starting with the people named as losing out.

## Sources

- UK Government Office for Science (2024). *The Futures Toolkit*, 2nd edition, pp. 91–96 and 113. The definition, present bias, the seven steps, control scoring, the questions for events in and out of control, and the forward-and-backward quick version. (`go-science-2024-toolkit`)
- Inayatullah, S. (2008). Six pillars: futures thinking for transforming. *Foresight*, 10(1), 4–21, p. 18. Elise Boulding's origin of the technique, memories of the future, backcasting a worst case, and plan versus action learning. (`inayatullah-2008-six-pillars`)
- Robinson, J. B. (1982). Energy backcasting: A proposed method of policy analysis. *Energy Policy*, 10(4), 337–344. The energy-policy paper usually cited for the method. Named only; no claim here rests on it until the text is checked (see `SOURCES.md`).

Every claim above is tied to a page in `references/provenance.md`.

## See Also

- `references/workshop-guide.md` — running a backcast with a group
- `references/provenance.md` — where each element of this skill comes from
