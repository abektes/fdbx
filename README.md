# fdbx — Futures Design Box

**Futures-thinking methods for designers. Every claim traces to a page you can open.**

---

## What this is

fdbx is a set of AI skills that bring published futures-studies methods into design work. It is the sibling of [edbx](https://github.com/abektes/edbx-designskills) (ethical design) and is built the same way: one `SKILL.md` per method, a router, plain-language tutorials, and the same evaluation harness.

fdbx does not predict the future. Its methods widen the futures a team takes seriously, surface what a brief assumes about the future, and connect that to what to do now.

## What's different from edbx

**Provenance you can check.** Each skill has a `references/provenance.md` table. Every element the skill attributes to a source has a row with the source, the printed page (or section), and a short anchor phrase from that page. `scripts/check_provenance.py` confirms each anchor is actually on the cited page. It reports the real page if it is somewhere else, and fails if it is nowhere.

```bash
python3 scripts/fetch_sources.py       # download the papers listed in sources/manifest.json
python3 scripts/check_provenance.py    # 251 anchors across 6 skills, 0 problems
```

The papers are not in the repo (most are copyrighted). The fetch script rebuilds the library from the manifest. See [`SOURCES.md`](SOURCES.md) for the bibliography, sources cited but not yet checked, and discrepancies found between sources.

**Every output ends with an Evidence Ledger and a Handoff.** Futures work runs on claims about trends and signals, and a model states those fluently whether or not they are true. The ledger tags every such claim as user-supplied, sourced, or an assumption. The handoff names the next fdbx or edbx method. See [`docs/conventions.md`](docs/conventions.md).

**Adaptations are labelled.** Where fdbx adds something the source does not describe, such as pointing CLA at a design brief, the skill marks it as an fdbx adaptation, not as the author's method.

## Skills

| Skill | Source | What it does |
|---|---|---|
| [`fdbx-horizon-scanning`](fdbx/fdbx-horizon-scanning/) | GO-Science 2024 | Collects signals of change from sources the user supplies or a live search finds (never from model memory), clusters them into a natural agenda, and picks the drivers worth acting on |
| [`fdbx-causal-layered-analysis`](fdbx/fdbx-causal-layered-analysis/) | Inayatullah 1998, 2008 | Reads a brief at four depths (litany, social causes, worldview, myth/metaphor) and climbs back up to a reframed brief |
| [`fdbx-futures-triangle`](fdbx/fdbx-futures-triangle/) | Inayatullah 2008 | Maps the images of the future that pull, the trends that push, and the weights holding each image back |
| [`fdbx-four-futures`](fdbx/fdbx-four-futures/) | Dator 2009 | Puts the product in four fundamentally different futures (Continued Growth, Collapse, Discipline, Transformation) with no best, worst or likely case |
| [`fdbx-three-horizons`](fdbx/fdbx-three-horizons/) | Sharpe et al. 2016; Curry & Hodgson 2008 | Maps the declining H1, emerging H3 and turbulent H2, and sorts innovations into H2+ and H2− (not the McKinsey model) |
| [`fdbx-backcasting`](fdbx/fdbx-backcasting/) | GO-Science 2024; Inayatullah 2008 | Works back from a preferred future to today, scores each critical event by how much the team controls it, names who loses out, and ends in an action plan |
| [`fdbx`](fdbx/fdbx/) | — | Router: which method, in what order, and when to hand off to edbx |

Tutorials: [`tutorials/`](tutorials/).

## Status

Version 0.1. The skills are written and pass the structural and provenance gates. A **baseline probe** (36 outputs from DeepSeek V4 Pro with no skill loaded) found that the plain model already knows these methods well, but states present-day facts without sources and invents facts about the user's own situation. It also skips each method's action structure: who acts per layer, Dator's exercise questions, per-image weights, and H2+/−. With the skills loaded, those steps appear in 8–9 of 9 outputs per skill, and every output has an Evidence Ledger with 98–100% of rows correctly typed (this took one fix to the skills; see the probe notes). The ledger labels invented claims rather than removing them, and the body can still assert what the ledger calls an assumption. In a partially blind side-by-side review of all 12 scenarios, one reviewer (the fdbx owner) preferred the with-skill output in 12 of 12 pairs. Because that reviewer commissioned the skills and the blinding was partial, an independent review is next. See [`docs/baseline-probe-batch-1.md`](docs/baseline-probe-batch-1.md).

**Batch 2** probed five more methods before writing any skill. The plain model already handles the Futures Wheel, Design Fiction and the Futures Cone well, so they were set aside (`candidates/`). Two were written: **Backcasting**, where the plain model often planned forward and invented the user's current figures, and **Horizon Scanning**, where it gave no sources at all and added figures to signals the user supplied. With the skills, each method's own steps appear in 9/9 outputs. The probe also showed a skill *introducing* a failure: asked for sources, one output invented 14 URLs. Tightening what counts as `sourced` (a URL in the row, from the user or a search) cut outputs with `sourced` claims from 9/54 to 2/54 across all six skills. With live search, Horizon Scanning cited 54 links in its final run, every one taken from the search results, and the figures checked against their sources matched. See [`docs/baseline-probe-batch-2.md`](docs/baseline-probe-batch-2.md).

All six skills are also scored against their own quality bars with `conformance.json` rubrics: code for counts and structure, and TypeSafe Jev for judgments, calibrated against hand labels (100% agreement on decided cases in both batches). Every quality bar is covered. Pass rates: Futures Triangle and Four Futures 100%, Backcasting 98%, Causal Layered Analysis 96%, Three Horizons 91%, Horizon Scanning 89%. The real failures are few and named in the probe notes. One was fixed and measured: CLA left the Myth row's solution and problem-solver empty in 7 of 36 outputs, and in none after the fix (p = 0.01). A Jev citation check found 15 of 154 cited claims unsupported by their search excerpt. The calibration labels are by the skills' author and are tracked in `eval-framework/calibration/` for a second reader.

## Install

fdbx is a Claude Code plugin and its own plugin marketplace. In Claude Code:

```
/plugin marketplace add abektes/fdbx
/plugin install fdbx@fdbx
```

Or from a terminal, the same two steps:

```bash
claude plugin marketplace add abektes/fdbx && claude plugin install fdbx@fdbx
```

From a clone, `./install-skills.sh` does this for you (`--local` installs from the checkout). To try it for one session without installing: `claude --plugin-dir /path/to/fdbx`.

The plugin adds seven skills and one agent:

| | How to call it |
|---|---|
| The six methods | `/fdbx:horizon-scanning`, `/fdbx:causal-layered-analysis`, `/fdbx:futures-triangle`, `/fdbx:four-futures`, `/fdbx:three-horizons`, `/fdbx:backcasting` |
| The router | `/fdbx:help`: describe your situation, get the method and the order to run them in |
| The Futures Design Specialist agent | `claude --agent fdbx:futures-design-specialist`, or pick it in `/agents`. It asks what kind of futures work you are doing, routes to a method, runs it, and redirects requests for predictions or remembered figures. Defined in [`AGENT.md`](AGENT.md). |

Update with `claude plugin marketplace update fdbx && claude plugin update fdbx@fdbx`; remove with `claude plugin uninstall fdbx@fdbx`.

Without Claude Code, point any AI assistant at this repo so it reads `AGENT.md`, or load one skill's `SKILL.md` as a system prompt.

## Checks

```bash
python3 -m unittest discover -s tests       # harness tests
python3 scripts/validate_skills.py          # frontmatter, links, house style, fdbx rules
python3 scripts/lint_template_gaps.py       # every quality-bar item has an output slot
python3 scripts/check_provenance.py         # every sourced claim is on its cited page
claude plugin validate .claude-plugin/plugin.json       # plugin manifest
claude plugin validate .claude-plugin/marketplace.json  # marketplace manifest
python3 scripts/check_agent_routing.py      # the agent routes 10 situations (uses your Claude login)
```

`validate_skills.py` reports five warnings about `skills/` symlink names. They are the same as edbx's: the plugin invokes skills by short name on purpose.

## Repository layout

```
.
├── fdbx/                  one folder per skill: SKILL.md, references/ (incl. provenance.md), assets/, evals/
├── AGENT.md               the Futures Design Specialist agent (any AI tool)
├── agents/                the same agent, as a Claude Code plugin subagent
├── .claude-plugin/        plugin.json and marketplace.json
├── skills/                symlinks the plugin loader walks (/fdbx:<name>)
├── candidates/            eval scenarios for methods probed but not yet written
├── tutorials/             plain-language guide per method
├── sources/manifest.json  where each source comes from; the files themselves are fetched locally
├── SOURCES.md             bibliography, cite-only list, discrepancies
├── scripts/               box.py (the only box-specific file), fetcher, provenance gate, edbx harness
├── tests/                 unittest suite
└── docs/                  conventions and plans
```

## Acknowledgements

The methods belong to their authors: Sohail Inayatullah (Causal Layered Analysis, the Futures Triangle), Jim Dator and the Hawaii Research Center for Futures Studies (the four generic futures), Bill Sharpe, Anthony Hodgson, Andrew Curry and the International Futures Forum (Three Horizons), Elise Boulding (backcasting, as credited by Inayatullah), and the UK Government Office for Science, whose *Futures Toolkit* is the procedural source for horizon scanning and backcasting. fdbx's contribution is integration: making these methods runnable by AI at the moment a design decision is made, with a trail back to the source.

## License

MIT for the fdbx code and skill text. Sources remain under their own terms; see `sources/manifest.json`.
