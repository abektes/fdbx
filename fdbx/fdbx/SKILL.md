---
name: fdbx
description: Futures-thinking guide for designers. Describe your brief, product, or decision and get routed to the right fdbx method — Horizon Scanning, Causal Layered Analysis, Futures Triangle, Four Futures, Three Horizons, or Backcasting — and the order to run them in. Use when you don't know which fdbx:* skill to start with, when a roadmap assumes a single future, or when you want to widen the time horizon of a design decision before committing.
version: "0.2"
tags: [futures, router]
---

# Futures Design Guide

## Overview

A router for the fdbx methods. Each method is a published futures-studies technique, adapted for design work, with every claim traced to a page in its source through a provenance table inside each skill, checked by `scripts/check_provenance.py`.

fdbx does not predict the future. Its methods widen the range of futures a team takes seriously, surface what a brief assumes about the future, and connect that to decisions made now.

## Use This Skill When

- You have a futures question and don't know which method fits
- You want a recommended sequence of methods
- You want to hand a futures output to an edbx method, or the reverse

## Inputs

- The brief, product, service or decision
- The time horizon you care about, if known
- What prompted the question ("the roadmap only has one future", "we keep designing the same thing", "we need a transition plan")

## Workflow

### 1. Identify what the user is really asking

| The user says… | They need to… |
|---|---|
| "What is changing out there?" / "what do these signals add up to?" | **Scan** for signals |
| "Is this even the right brief?" / "we keep designing the same thing" | **Deepen** the problem |
| "What forces are shaping this?" / "which future are we designing for?" | **Map** the forces |
| "What if the future isn't what we assume?" / "our plan has one future in it" | **Experience alternatives** |
| "How do we get from today's model to the next?" / "which of our innovations matter?" | **Plan the transition** |
| "We have a goal for 2035; what do we do now?" / "our roadmap stops short of the vision" | **Work back** from a chosen future |

If it is unclear, ask one question before routing.

### 2. Route

| Need | Skill |
|---|---|
| Scan | `/fdbx:horizon-scanning` |
| Deepen | `/fdbx:causal-layered-analysis` |
| Map | `/fdbx:futures-triangle` |
| Experience alternatives | `/fdbx:four-futures` |
| Plan the transition | `/fdbx:three-horizons` |
| Work back | `/fdbx:backcasting` |

### 3. Chains

- **Full sequence:** horizon-scanning → causal-layered-analysis → futures-triangle → four-futures → three-horizons → backcasting. Gather real signals, deepen the problem, map the forces, experience the alternatives, plan the transition, then work back from the preferred future to today's actions.
- **Scan first when the inputs are thin.** The other methods need claims about the present. Horizon-scanning supplies them with sources, so fewer end up as assumptions in the Evidence Ledger.
- **Before any scenario work, run CLA.** Inayatullah recommends it before scenario building, so that scenarios differ in depth, not only in degree.
- **Triangle → Four Futures:** the triangle's images and pushes become material for the four generic futures.
- **Four Futures → Three Horizons:** the preferred-future sketch becomes a candidate third horizon.
- **Four Futures → Backcasting:** the preferred-future sketch is the end state to work back from. A feared future can be backcast in avoid mode.

### 4. Cross-box handoffs to edbx

| From fdbx | To edbx | Why |
|---|---|---|
| A future from four-futures | `edbx:black-mirror-brainstorming`, `edbx:stf-et` | What harm could the product cause in that world? |
| Robust design decisions (four-futures) | `edbx:worrystorming` | Check them before committing |
| Reframed brief (CLA) | `edbx:anotherlens`, `edbx:worrystorming` | Whose view is still missing; what the new frame might harm |
| Three Horizons dilemma | `edbx:value-dams-and-flows` | Map the stakeholder value conflict behind it |
| Three Horizons actions | `edbx:pledge-works`, `edbx:ethical-contract` | Turn them into accountable commitments |
| Backcasting action plan | `edbx:pledge-works`, `edbx:worrystorming` | Commit to the plan; start with the people it names as losing out |
| A high-impact driver (horizon-scanning) | `edbx:stf-et`, `edbx:worrystorming` | Whom could this change harm? |

## Guardrails

- Do not present any fdbx output as a prediction.
- Do not invent method steps that are not in the routed skill's `SKILL.md`.
- Every fdbx output ends with an Evidence Ledger and a Handoff. If a user asks to skip them, keep the ledger: it is what separates sourced claims from model assumptions.

## Sources

Each routed skill lists its own sources and provenance. The full bibliography, including sources cited but not yet checked, is in `SOURCES.md` at the repository root.
