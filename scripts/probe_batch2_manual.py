#!/usr/bin/env python3
"""Per-output reads for batch 2 that a single regex cannot make: whether a
Backcasting timeline really runs backwards, and whether Horizon Scanning adds
figures to user-supplied signals. Results are recorded in
docs/baseline-probe-batch-2.md.

    python3 scripts/probe_batch2_manual.py <run id>
"""
import json, re, sys
from box import EVAL_DIR
run=sys.argv[1]
m=json.load(open(EVAL_DIR / 'runs' / f'{run}.json'))
docs=[json.load(open(EVAL_DIR / 'generations' / f"{t['key']}.json")) for t in m['tasks']]
print("BACKCASTING: year order of Backward Timeline rows")
for d in docs:
    if d['skill']!='fdbx-backcasting': continue
    o=d['output']; i=o.find('Backward Timeline'); sec=o[i:i+5000]
    j=re.search(r'(?m)^#{2,4} (?!Backward)',sec[20:]); sec=sec[:j.start()+20] if j else sec
    yrs=[int(y) for y in re.findall(r'(?m)^\|\s*\**(?:~|c\.)?\s*(20\d\d)',sec)]
    back = all(a>=b for a,b in zip(yrs,yrs[1:])) and len(yrs)>2
    unk = len(re.findall(r'(?i)unknown',o))
    print(f"  {d['scenario'][:24]:24} {d['rep']} years={yrs[:8]} backward={back} 'unknown' mentions={unk}")
print("HORIZON: library figures added to user signals; leads separated; mode")
for d in docs:
    if d['skill']!='fdbx-horizon-scanning': continue
    o=d['output']
    mode=re.search(r'(?i)\*\*Mode[^*]*\*\*:?\s*([^\n]{0,70})',o)
    i=o.find('Leads to Verify'); 
    if d['scenario'].startswith('library'):
        fig=re.findall(r'(?i)[^\n]{0,50}(?:footfall|wi-?fi|sessions|visits)[^\n]{0,40}\d+\s?%',o)
    else: fig='n/a'
    print(f"  {d['scenario'][:24]:24} {d['rep']} mode={mode.group(1).strip()[:50] if mode else None!r} leads_section={i>0} added_figs={fig if fig=='n/a' else len(fig)}")
