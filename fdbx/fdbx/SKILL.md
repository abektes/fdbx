---
name: fdbx
description: Futures-thinking guide for designers. Describe your brief, product, or decision and get routed to the right fdbx method — Causal Layered Analysis, Futures Triangle, Four Futures, or Three Horizons — and the order to run them in. Use when you don't know which fdbx:* skill to start with, when a roadmap assumes a single future, or when you want to widen the time horizon of a design decision before committing.
version: "0.1"
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
| "Is this even the right brief?" / "we keep designing the same thing" | **Deepen** the problem |
| "What forces are shaping this?" / "which future are we designing for?" | **Map** the forces |
| "What if the future isn't what we assume?" / "our plan has one future in it" | **Experience alternatives** |
| "How do we get from today's model to the next?" / "which of our innovations matter?" | **Plan the transition** |

If it is unclear, ask one question before routing.

### 2. Route

| Need | Skill |
|---|---|
| Deepen | `/fdbx:causal-layered-analysis` |
| Map | `/fdbx:futures-triangle` |
| Experience alternatives | `/fdbx:four-futures` |
| Plan the transition | `/fdbx:three-horizons` |

### 3. Chains

- **Full sequence:** causal-layered-analysis → futures-triangle → four-futures → three-horizons. Deepen the problem, map the forces, experience the alternatives, then plan the transition to the preferred one.
- **Before any scenario work, run CLA.** Inayatullah recommends it before scenario building, so that scenarios differ in depth, not only in degree.
- **Triangle → Four Futures:** the triangle's images and pushes become material for the four generic futures.
- **Four Futures → Three Horizons:** the preferred-future sketch becomes a candidate third horizon.

### 4. Cross-box handoffs to edbx

| From fdbx | To edbx | Why |
|---|---|---|
| A future from four-futures | `edbx:black-mirror-brainstorming`, `edbx:stf-et` | What harm could the product cause in that world? |
| Robust design decisions (four-futures) | `edbx:worrystorming` | Check them before committing |
| Reframed brief (CLA) | `edbx:anotherlens`, `edbx:worrystorming` | Whose view is still missing; what the new frame might harm |
| Three Horizons dilemma | `edbx:value-dams-and-flows` | Map the stakeholder value conflict behind it |
| Three Horizons actions | `edbx:pledge-works`, `edbx:ethical-contract` | Turn them into accountable commitments |

## Guardrails

- Do not present any fdbx output as a prediction.
- Do not invent method steps that are not in the routed skill's `SKILL.md`.
- Every fdbx output ends with an Evidence Ledger and a Handoff. If a user asks to skip them, keep the ledger: it is what separates sourced claims from model assumptions.

## Sources

Each routed skill lists its own sources and provenance. The full bibliography, including sources cited but not yet checked, is in `SOURCES.md` at the repository root.
