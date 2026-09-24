# Candidate methods, probed but not yet written

These methods were probed in batch 2 (`docs/baseline-probe-batch-2.md`) and
set aside because the plain model already does most of what a skill would add.
Their eval scenarios are kept here so the probe can be repeated or extended.

| Method | Probe method name (the H1 the baseline used) | Source in the library |
|---|---|---|
| Futures Cone | `Futures Cone` | `voros-2017-futures-cone` |
| Futures Wheel | `Futures Wheel` | `glenn-2009-futures-wheel`, `go-science-2024-toolkit` pp. 75–78 |
| Design Fiction | `Design Fiction` | `bleecker-2009-design-fiction`, `go-science-2024-toolkit` pp. 102–107 |

To re-probe one, move its folder into `fdbx/`, add a `SKILL.md` whose first
heading is the method name above, and run
`python3 scripts/run_generation.py --skills <name> --arm without_skill --reps 3`.
The baseline cache key depends only on the method name and the prompts, so the
existing outputs are reused. Remove the placeholder before running the validator.
