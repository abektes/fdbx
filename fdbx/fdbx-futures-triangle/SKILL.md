---
name: fdbx-futures-triangle
description: Use when a team needs to see the forces shaping the future of a product, service, sector, or place before deciding what to design for — apply Inayatullah's Futures Triangle to map the images of the future that pull, the trends and drivers that push, and the barriers that weigh each image down, then derive a plausible future and scenarios. Trigger for "futures triangle", "pull push weight", "what forces shape this", "which future are we designing for", "images of the future", "drivers and trends", "what's holding this back", "used future", or when a roadmap assumes one direction without saying why.
version: "0.1"
tags: [futures, mapping]
---

# Futures Triangle

## Overview

The Futures Triangle is a mapping tool from Sohail Inayatullah's *Six Pillars* approach to futures thinking. It maps how people see the future of an issue today through three forces:

- **Pull** — the images of the future that draw people forward. Inayatullah identifies about five that recur as archetypes: *evolution and progress*, *collapse*, *Gaia*, *globalism*, and *back to the future*.
- **Push** — the drivers and trends of the present that are already changing things. He describes these as quantitative: demographics, spending, adoption rates.
- **Weight** — the barriers to change. Each image of the future has its own weights: the structures, interests and habits that hold it back.

Analysing how the three interact helps a team develop a **plausible future**: the image that has pushes behind it and weights it can overcome. It also shows which hopeful images are pulling hard but are weighed down, and which trends are pushing toward a future nobody has chosen.

The triangle sits in the first pillar, *Mapping*. It is a way of seeing the present clearly before anticipating, deepening or creating alternatives.

> **fdbx adaptation:** we add a design question the source does not ask directly. Which image of the future is the current product strategy already serving, and is it a *used future*, borrowed without anyone deciding to? Inayatullah defines the used future and the disowned future on p. 5 of the same paper; we apply both concepts to the strategy.

## Use This Skill When

- A roadmap or brief assumes a direction ("the market is moving to…") without showing why.
- The team needs a shared picture of what is driving change in its sector.
- Stakeholders hold different visions of the future and nobody has put them side by side.
- You want scenarios grounded in the forces at play, not in the team's preferences.
- You suspect the product is designed for a future borrowed from somewhere else.

## Inputs

- The issue, product, service, sector or place, and a time horizon (a year, e.g. 2040).
- Whose views matter: users, staff, regulators, competitors, communities, critics.
- Any trends, data or research the user has. These go into the Evidence Ledger as `user-supplied` or `sourced`.
- The current strategy or roadmap, if the user wants to know which future it serves.

## Workflow

### Step 1 — Frame

State the issue, the horizon year, and whose views are being mapped. Optionally open with Inayatullah's six futures questions to surface the team's own expectations first: what they predict, what they fear, what their prediction assumes, what the alternatives are, what they prefer, and what the next steps would be. The answers often reveal the image the team already holds.

### Step 2 — Pull: images of the future

List the images of the future that people actually hold for this issue, with **who holds each one**. Map each to an archetype where it fits:

| Archetype | Core belief |
|---|---|
| Evolution and progress | More technology and rationality lead forward |
| Collapse | Limits have been reached or overshot; things get worse |
| Gaia | Repair and inclusion; partnership between people, nature and technology |
| Globalism | Borders and barriers fall; integration brings shared wealth |
| Back to the future | Return to a simpler, clearer, more ordered past |

The archetypes are a starting set, not a closed list. If an image does not fit, name it. Map **at least three** distinct images.

See `references/archetype-guide.md` for what each image tends to look like in product and service contexts.

### Step 3 — Push: drivers and trends

List the drivers and trends already changing the issue. Prefer quantitative ones: rates, shares, costs, counts. For each push, say which image(s) it pushes toward. Record every push in the Evidence Ledger with its type. A trend the model supplies from training data is an `assumption` until the user confirms or sources it.

### Step 4 — Weight: barriers per image

For each image, name what holds it back: infrastructure, regulation, business models, incumbent interests, skills, habits, beliefs. Weights differ between images. Something that blocks the Gaia image may be irrelevant to the progress image. Be specific: "legacy branch leases run to 2032", not "resistance to change".

### Step 5 — Analyse the interaction

For each image, weigh its pull (how widely held, how compelling), the pushes toward it, and the weights against it. Then state:

- the **plausible future**: the image with strong pushes and weights that can be overcome, and why
- **contested images**: strong pull, heavy weight
- **unchosen pushes**: trends driving toward a future no stakeholder is pulling for

### Step 6 — Scenarios from the triangle

Derive three or four short scenarios from the triangle, built around the images or around the main drivers (Inayatullah's multi-single-variable method). Each scenario names the image or driver it is built on.

### Step 7 — Design implications

> **fdbx adaptation.**

- **Which image does the current strategy serve?** Name it. Say whether it was chosen or borrowed — a *used future*.
- **What is the disowned future?** The image the organisation pushes away, which may be the one it most needs to look at.
- What would the design need to be to work in the plausible future, and what would change if a contested image won?

## Output Format

A blank version is in `assets/triangle-template.md`.

### Futures Triangle: [Issue] to [Year]

One paragraph: the issue, the horizon, whose views are mapped.

### Pull — Images of the Future

| Image | Archetype | Held by | What it promises |
|---|---|---|---|

### Push — Drivers and Trends

| Driver or trend | Direction and size | Pushes toward image(s) | Ledger ref |
|---|---|---|---|

### Weight — Barriers by Image

| Image | Weights holding it back |
|---|---|

### Interaction

**Plausible future:** … and why.
**Contested images:** …
**Unchosen pushes:** …

### Scenarios

1. **[Name]** — built on [image or driver]. …
2. …
3. …

### Design Implications

**Image the current strategy serves:** … **Chosen or used?** …
**Disowned future:** …
**What the design needs to be:** …

### Evidence Ledger

Type is one of `user-supplied` (stated in the brief or by the user), `sourced` (the Basis cell holds a URL the reader can open, which came from the user or from a search or tool result in this session; no URL, not `sourced`), or `assumption`. Anything that comes from model knowledge is an `assumption`, however confident it sounds, even when you can name the report or organisation it comes from. The ledger records claims about the world used as input, not this method's own sources. Do not use other types such as "trend" or "general knowledge".

| Claim used as input | Type | Basis |
|---|---|---|

### Handoff

**Assumptions surfaced:** …
**Open decisions:** …
**Suggested next method:** …

## Guardrails

- Every push goes in the Evidence Ledger with its type. A confident statistic from model memory is an `assumption`.
- Images must be held by someone. Name the holders; do not invent visions for the analysis to knock down.
- Do not fold every image into *evolution and progress*. For technology products it is the easiest image to see and the easiest to mistake for the only one.
- Weights are specific barriers, not general "resistance". If you cannot say what the barrier is, you have not found it yet.
- Weights differ by image. If every image has the same weights, the analysis has not been done per image.
- The triangle produces a *plausible* future, not a prediction. Say so in the output.
- The five archetypes are a starting set. Name a new image rather than forcing a fit.

## Deliverable Quality Bar

A strong Futures Triangle output:

- maps at least three distinct images of the future, each with an archetype (or a named new one) and who holds it
- lists at least four pushes, each with a direction or size, each linked to the image(s) it pushes toward
- gives weights for every image, and the weights differ between images
- names a plausible future and justifies it from pull, push and weight together
- derives three or four scenarios, each built on a named image or driver
- states which image the current strategy serves and whether it is chosen or used, and names a disowned future
- records every push and statistic in the Evidence Ledger with its type
- ends with a Handoff naming the next method and why

## Integration with Other Skills

- **fdbx-causal-layered-analysis** — explains *why* a weight is so heavy: weights often sit at the worldview and myth layers.
- **fdbx-four-futures** — use the triangle's images and pushes as material for the four generic futures.
- **fdbx-three-horizons** — the plausible future and contested images are candidate third horizons; the weights describe first-horizon lock-in.
- **edbx-value-dams-and-flows** — weights are often stakeholder value conflicts; map them there.
- **edbx-black-mirror-brainstorming** — run on an *unchosen push* to see where it leads if nobody steers it.

## Sources

- Inayatullah, S. (2008). Six pillars: futures thinking for transforming. *Foresight*, 10(1), 4–21. The futures triangle and its five archetypal images (pp. 7–8); multi-single-variable scenarios derived from the triangle (p. 15); the six futures questions (p. 7); the used and disowned futures (p. 5). (`inayatullah-2008-six-pillars`)

Every claim above is tied to a page in `references/provenance.md`.

## See Also

- `references/archetype-guide.md` — how the five images tend to show up in product and service work
- `references/provenance.md` — where each element of this skill comes from
