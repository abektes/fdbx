# Sources

Every fdbx skill is built from the sources below. Each skill's
`references/provenance.md` ties its claims to a page in one of them, and
`scripts/check_provenance.py` confirms each anchor phrase is on the cited page.
The files are not in this repo; `scripts/fetch_sources.py` downloads them from
the URLs in [`sources/manifest.json`](sources/manifest.json).

## Downloaded and checked

| Key | Source | Used by |
|---|---|---|
| `inayatullah-1998-cla` | Inayatullah, S. (1998). Causal layered analysis: Poststructuralism as method. *Futures*, 30(8), 815–829. [doi:10.1016/S0016-3287(98)00086-X](https://doi.org/10.1016/S0016-3287(98)00086-X). Full text on the author's site; no page numbers, cited by section. | causal-layered-analysis |
| `inayatullah-2008-six-pillars` | Inayatullah, S. (2008). Six pillars: futures thinking for transforming. *Foresight*, 10(1), 4–21. [doi:10.1108/14636680810855991](https://doi.org/10.1108/14636680810855991) | causal-layered-analysis, futures-triangle, four-futures |
| `dator-2009-manoa` | Dator, J. (2009). Alternative futures at the Manoa School. *Journal of Futures Studies*, 14(2), 1–18. [jfsdigital.org](https://jfsdigital.org/articles-and-essays/2009-2/vol-14-no-2-november/articles/futuristsalternative-futures-at-the-manoa-school/) | four-futures |
| `sharpe-2016-three-horizons` | Sharpe, B., Hodgson, A., Leicester, G., Lyon, A., & Fazey, I. (2016). Three horizons: a pathways practice for transformation. *Ecology and Society*, 21(2), 47. [doi:10.5751/ES-08388-210247](https://doi.org/10.5751/ES-08388-210247) | three-horizons |
| `curry-hodgson-2008-horizons` | Curry, A., & Hodgson, A. (2008). Seeing in multiple horizons: Connecting futures to strategy. *Journal of Futures Studies*, 13(1), 1–20. [jfsdigital.org](https://jfsdigital.org/articles-and-essays/2008-2/vol-13-no-1-august/articles/seeing-in-multiple-horizons-connecting-futures-to-strategy/) | three-horizons |
| `go-science-2024-toolkit` | UK Government Office for Science (2024). *The Futures Toolkit*, 2nd edition. Open Government Licence. | batch 2 (horizon scanning, backcasting) |
| `glenn-2009-futures-wheel` | Glenn, J. C. (2009). The Futures Wheel. In Glenn & Gordon (Eds.), *Futures Research Methodology 3.0*. The Millennium Project. | batch 2 (futures wheel) |
| `bleecker-2009-design-fiction` | Bleecker, J. (2009). *Design Fiction: A short essay on design, science, fact and fiction*. Near Future Laboratory. CC BY-NC-ND 3.0. | batch 2 (design fiction) |
| `voros-2017-futures-cone` | Voros, J. (2017). The Futures Cone, use and history. *The Voroscope*. | batch 2 (futures cone) |

## Cited but not downloaded

These are paywalled or blocked to scripts. They are named where the method
comes from them, but no fdbx claim rests on them until someone checks the text.

- Robinson, J. B. (1982). Energy backcasting: A proposed method of policy analysis. *Energy Policy*, 10(4), 337–344.
- Robinson, J. B. (1990). Futures under glass: A recipe for people who hate to predict. *Futures*, 22(8), 820–842.
- Voros, J. (2003). A generic foresight process framework. *Foresight*, 5(3), 10–21. [doi:10.1108/14636680310698379](https://doi.org/10.1108/14636680310698379)
- Hancock, T., & Bezold, C. (1994). Possible futures, preferable futures. *Healthcare Forum Journal*, 37(2), 23–29.
- Inayatullah, S. (2023). The futures triangle: Origins and iterations. *World Futures Review*. [doi:10.1177/19467567231203162](https://doi.org/10.1177/19467567231203162)
- Baghai, M., Coley, S., & White, D. (1999). *The Alchemy of Growth*. The management Three Horizons that the futures version departs from; described here only through Curry & Hodgson (2008).
- Candy, S. (2018). Gaming futures literacy: The Thing From The Future. In R. Miller (Ed.), *Transforming the Future*. UNESCO / Routledge.
- Dator, J. (1996/2019). What futures studies is, and is not. Source of "Dator's laws". Not verified against the text, so fdbx does not quote them.

## Discrepancies found while reading

- **Dator's third future.** Dator calls it *Discipline* (2009, pp. 1, 10). Inayatullah's summary of the same model calls it *Steady state* (2008, p. 16). fdbx uses Dator's name and notes the alias.
- **What "Transformation" means.** In Dator (2009, p. 10) it is technology-led and posthuman. Inayatullah (2008, pp. 16–17) allows a spiritual route too. fdbx keeps both and says whose is whose.
- **Two Three Horizons.** The management original (Baghai, Coley & White, 1999) draws successive growth curves. The futures version (Sharpe & Hodgson) has all three horizons present at once, with different influence (Curry & Hodgson 2008, pp. 4–5). fdbx implements the futures version only.
