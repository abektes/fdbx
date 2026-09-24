#!/usr/bin/env python3
"""Check every link a generation cites, for runs made with --web-search.

A skill that asks for sources can make a model invent them (batch 2 found one
output with 14 made-up URLs; docs/baseline-probe-batch-2.md). This checks each
URL in an output three ways:

  in_search  the URL was among the search results the model was given
  opens      it resolves over HTTP (403/429 from bot blocking is "blocked", not "dead")
  supports   the claim's content words appear in the search excerpt or the page

`supports` is word overlap, so it only flags rows to read; it does not decide them.

    python3 scripts/check_links.py <run id> [--no-fetch]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import tempfile
import urllib.error
import urllib.request
from collections import Counter

from box import EVAL_DIR

# Markdown links first, allowing one level of parentheses inside the URL
# (EPRS_BRI(2023)746128); then bare URLs.
MD_URL_RE = re.compile(r"\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)")
URL_RE = re.compile(r"https?://[^\s)\]>|\"'`]+")
STOP = set("""a an and are as at be by for from has have in into is it its of on or that the this
to was were will with which who how what why their they not can could may more most new over
than such these those our your per via also been being about after before between both""".split())
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Safari/605.1.15"


def norm(url: str) -> str:
    url = url.rstrip(".,;:").split("#")[0]
    url = re.sub(r"^https?://(www\.)?", "", url.lower())
    url = re.sub(r"[?&]utm_[^&]+", "", url)
    return url.rstrip("/")


def words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9\-]{2,}", text.lower()) if w not in STOP}


def fetch(url: str) -> tuple[str, str]:
    """(status, page text). Status is ok / blocked / dead / error."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read(100_000_000)  # council PDFs can exceed 20 MB
            is_pdf = body[:5] == b"%PDF-" or "pdf" in (r.headers.get("Content-Type") or "")
    except urllib.error.HTTPError as e:
        return ("blocked" if e.code in (401, 403, 429, 451, 999) else "dead"), f"HTTP {e.code}"
    except Exception as e:  # DNS failure, TLS, timeout
        return "error", type(e).__name__
    if is_pdf:
        # Raw PDF bytes contain digits and fragments that "match" anything.
        with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
            f.write(body)
            f.flush()
            out = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True)
        return ("ok", out.stdout) if out.returncode == 0 else ("error", "pdftotext failed")
    raw = body.decode("utf-8", "replace")
    raw = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", raw)
    return "ok", html.unescape(re.sub(r"<[^>]+>", " ", raw))


def claim_for(output: str, url: str) -> str:
    """The table row or line that cites the URL, minus the URL and markup."""
    for line in output.splitlines():
        if url in line:
            line = line.replace(url, " ")
            return re.sub(r"[|*`\[\]()]", " ", line)
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("run")
    ap.add_argument("--no-fetch", action="store_true", help="skip HTTP checks")
    args = ap.parse_args()

    manifest = json.loads((EVAL_DIR / "runs" / f"{args.run}.json").read_text())
    page_cache: dict[str, tuple[str, str]] = {}
    totals: dict[str, Counter] = {}
    flagged: list[str] = []

    for t in manifest["tasks"]:
        d = json.loads((EVAL_DIR / "generations" / f"{t['key']}.json").read_text())
        out = d["output"]
        results = {norm(r["url"]): r for r in d.get("search_results", [])}
        md = MD_URL_RE.findall(out)
        bare = [u for u in URL_RE.findall(out) if not any(m.startswith(u) for m in md)]
        urls = list(dict.fromkeys(u.rstrip(".,;:") for u in md + bare))
        sourced_rows = re.findall(r"(?im)^\|[^\n]*\|[`*\s]*sourced[`*\s]*\|[^\n]*$", out)
        c = totals.setdefault(f"{d['skill']} / {d['arm']}", Counter())
        c["outputs"] += 1
        c["search results given"] += len(results)
        c["sourced rows"] += len(sourced_rows)
        c["sourced rows without URL"] += sum("http" not in r for r in sourced_rows)
        label = f"{d['scenario']} #{d['rep']}"

        for url in urls:
            c["URLs cited"] += 1
            hit = results.get(norm(url))
            c["in search results"] += bool(hit)
            claim = words(claim_for(out, url))
            evidence = (hit or {}).get("content") or ""
            status = "skipped"
            if not args.no_fetch:
                if url not in page_cache:
                    page_cache[url] = fetch(url)
                status, page = page_cache[url]
                c[f"opens: {status}"] += 1
                if status == "ok":
                    evidence += " " + page
            overlap = len(claim & words(evidence)) / len(claim) if claim else 0.0
            supported = overlap >= 0.5
            c["supported (>=50% of claim words found)"] += supported
            if not hit or status in ("dead", "error") or not supported:
                why = ", ".join(x for x, bad in (("not in search results", not hit),
                                                 (f"link {status}", status in ("dead", "error")),
                                                 (f"overlap {overlap:.0%}", not supported)) if bad)
                flagged.append(f"  {d['skill'][5:]} {d['arm']} {label}: {url}\n      {why}")

    for group, c in sorted(totals.items()):
        print(f"\n## {group}")
        for k in ("outputs", "search results given", "sourced rows", "sourced rows without URL",
                  "URLs cited", "in search results", "opens: ok", "opens: blocked", "opens: dead",
                  "opens: error", "supported (>=50% of claim words found)"):
            if k in c or k in ("URLs cited", "in search results"):
                print(f"  {k:42} {c[k]}")
    print(f"\n## Flagged for reading ({len(flagged)})")
    print("\n".join(flagged) if flagged else "  none")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
