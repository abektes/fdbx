#!/usr/bin/env python3
"""Generate skill-guided and baseline outputs for the A/B evaluation.

Lives in tracked `scripts/` on purpose. The previous harness lived inside the
gitignored `eval-framework/` tree and was lost, which is why RESULTS.md's numbers
are not reproducible. Outputs stay gitignored; the code that makes them does not.

The A/B follows RESULTS.md: both arms use the same generator, and the baseline is
told the method's name, so the comparison answers "does SKILL.md earn its tokens"
rather than "is a skill better than nothing".

    python3 scripts/run_generation.py --dry-run
    python3 scripts/run_generation.py --skills value-dams-and-flows,stf-et
    python3 scripts/run_generation.py --workers 8

Results are content-addressed and resumable: rerunning skips anything already
generated. The baseline cache key deliberately excludes SKILL.md, so editing a
skill does not invalidate its baseline -- every sweep after the first is half price.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import http.client
import json
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from box import BASELINE_ROLE, BOX, EVAL_DIR, REPO, SKILLS_DIR, evals_path, short as short_name
CACHE_DIR = EVAL_DIR / "generations"
RUNS_DIR = EVAL_DIR / "runs"

ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
DEFAULT_MAX_TOKENS = 64000
# OpenRouter serves one model from many providers. Scanning 357 generations for
# mangled common words ("Commitmennt", "Veriffication") found exactly two corrupted
# outputs, both served by Baidu, out of 38 it served; 0 of 319 from the other twelve.
IGNORE_PROVIDERS = ["Baidu"]

BASELINE_SYSTEM = (
    f"You are an expert {BASELINE_ROLE} assistant. Apply the {{method}} method thoroughly "
    "to the user's task. Produce a complete, well-structured output with all the "
    "standard sections that a {method} session would include."
)
SKILL_SYSTEM = (
    "You have been given a skill definition. Follow its workflow, output format, and "
    "guardrails exactly when responding to the user's task.\n\n{skill_md}"
)


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    path = EVAL_DIR / ".env"
    if not path.is_file():
        sys.exit(f"missing {path}")
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


@dataclass
class Task:
    skill: str
    scenario: str
    arm: str  # "with_skill" | "without_skill"
    prompt: str
    system: str
    model: str
    rep: int = 0
    web_search: int = 0  # max results from OpenRouter's web plugin; 0 = no search
    key: str = field(default="")

    def __post_init__(self) -> None:
        # The baseline's system prompt contains only the method name, so its key is
        # naturally independent of SKILL.md content and survives skill edits.
        digest = hashlib.sha256()
        for part in (self.model, self.arm, self.system, self.prompt):
            digest.update(part.encode())
            digest.update(b"\x00")
        # Generation is stochastic, so one sample cannot tell a fix from luck.
        # Rep 0 hashes exactly as before, keeping every existing cache entry valid.
        if self.rep:
            digest.update(f"rep={self.rep}".encode())
        # Same rule for search: runs without it keep their existing keys.
        if self.web_search:
            digest.update(f"web={self.web_search}".encode())
        self.key = digest.hexdigest()[:16]

    @property
    def label(self) -> str:
        suffix = f"#{self.rep}" if self.rep else ""
        web = "+web" if self.web_search else ""
        return f"{self.skill}/{self.scenario}/{self.arm}{web}{suffix}"


def read_skill(skill_dir: Path, ref: str | None = None) -> str:
    """SKILL.md as it is on disk, or as of a git ref for before/after comparisons.

    Generating the "before" arm after a skill has been edited needs the old text.
    Reading it from git keeps the working tree untouched and, because cache keys
    hash the content, reuses any generation already made from that exact version.
    """
    if ref is None:
        return (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    rel = (skill_dir / "SKILL.md").relative_to(REPO)
    out = subprocess.run(["git", "-C", str(REPO), "show", f"{ref}:{rel}"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"cannot read {rel} at {ref}: {out.stderr.strip()}")
    return out.stdout


def method_name(skill_md: str, fallback: str) -> str:
    """Human-readable method name, taken from the SKILL.md H1."""
    for line in skill_md.splitlines():
        if line.startswith("# "):
            return re.sub(r"\s*\(.*?\)\s*$", "", line[2:]).strip()
    return fallback


def build_tasks(
    skills: list[str] | None, scenarios: int | None, model: str,
    reps: int = 1, arms: tuple[str, ...] = ("without_skill", "with_skill"),
    skill_ref: str | None = None, web_search: int = 0,
) -> list[Task]:
    tasks: list[Task] = []
    for skill_dir in sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir()):
        name = skill_dir.name
        if name == BOX:  # the router produces no deliverable to grade
            continue
        short = short_name(name)
        if skills and short not in skills and name not in skills:
            continue

        eval_file = evals_path(name)
        if not eval_file.is_file():
            print(f"  ! {name}: no evals.json, skipping", file=sys.stderr)
            continue

        skill_md = read_skill(skill_dir, skill_ref)
        method = method_name(skill_md, name)
        entries = json.loads(eval_file.read_text())["evals"]
        if scenarios is not None:
            entries = entries[:scenarios]

        for entry in entries:
            # The eval sets drifted: 19 skills carry `name`, dah-cards does not, and
            # stf-et adds `expectations`. Fall back to the id rather than crash.
            scenario = entry.get("name") or f"eval-{entry.get('id', len(tasks))}"
            for arm, system in (
                ("without_skill", BASELINE_SYSTEM.format(method=method)),
                ("with_skill", SKILL_SYSTEM.format(skill_md=skill_md)),
            ):
                if arm not in arms:
                    continue
                for rep in range(reps):
                    tasks.append(
                        Task(
                            skill=name,
                            scenario=scenario,
                            arm=arm,
                            prompt=entry["prompt"],
                            system=system,
                            model=model,
                            rep=rep,
                            web_search=web_search,
                        )
                    )
    return tasks


def call_model(task: Task, api_key: str, max_tokens: int, attempts: int = 5) -> dict:
    request_body = {
        "model": task.model,
        "messages": [
            {"role": "system", "content": task.system},
            {"role": "user", "content": task.prompt},
        ],
        "max_tokens": max_tokens,
        "provider": {"ignore": IGNORE_PROVIDERS},
    }
    if task.web_search:
        # OpenRouter runs one Exa search on the conversation and puts the results
        # in the model's context; they come back as url_citation annotations, which
        # scripts/check_links.py compares against the URLs the output cites.
        request_body["plugins"] = [{"id": "web", "engine": "exa", "max_results": task.web_search}]
    payload = json.dumps(request_body).encode()

    last_error = ""
    for attempt in range(attempts):
        request = urllib.request.Request(
            ENDPOINT,
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        started = time.time()
        try:
            with urllib.request.urlopen(request, timeout=900) as response:
                body = json.loads(response.read())
        except urllib.error.HTTPError as exc:
            last_error = f"HTTP {exc.code}: {exc.read().decode()[:200]}"
            if exc.code not in (408, 429, 500, 502, 503, 504, 529):
                raise RuntimeError(last_error) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
                http.client.HTTPException, ConnectionError) as exc:
            # IncompleteRead (a dropped connection mid-body) is an HTTPException,
            # and was failing tasks outright instead of being retried.
            last_error = f"{type(exc).__name__}: {exc}"
        else:
            choice = body["choices"][0]
            text = choice["message"].get("content") or ""
            finish = choice.get("finish_reason")
            if not text.strip():
                # A reasoning model can exhaust max_tokens before emitting an answer.
                last_error = f"empty content (finish_reason={finish})"
            elif finish != "stop":
                # "error" means the upstream provider died mid-stream and "length"
                # means truncation. Either way the document is a fragment, and
                # scoring a fragment reports a skill failure that never happened.
                last_error = f"incomplete generation (finish_reason={finish}, {len(text)} chars)"
            else:
                usage = body.get("usage", {})
                details = usage.get("completion_tokens_details") or {}
                return {
                    "output": text,
                    "elapsed_seconds": round(time.time() - started, 1),
                    "requested_model": task.model,
                    # Log what actually served the request: OpenRouter aliases move,
                    # and a run whose model is unrecorded is not reproducible.
                    "served_model": body.get("model"),
                    "provider": body.get("provider"),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "reasoning_tokens": details.get("reasoning_tokens", 0),
                    "cost_usd": usage.get("cost", 0.0),
                    "finish_reason": choice.get("finish_reason"),
                    "attempts": attempt + 1,
                    "web_search": task.web_search,
                    "search_results": [
                        {k: a["url_citation"].get(k) for k in ("url", "title", "content")}
                        for a in choice["message"].get("annotations") or []
                        if a.get("type") == "url_citation"
                    ],
                }

        if attempt < attempts - 1:
            time.sleep(min(60, 2**attempt) + random.uniform(0, 1))

    raise RuntimeError(f"{task.label}: gave up after {attempts} attempts — {last_error}")


def run(task: Task, api_key: str, max_tokens: int) -> tuple[Task, dict, bool]:
    cached = CACHE_DIR / f"{task.key}.json"
    if cached.is_file():
        return task, json.loads(cached.read_text()), True

    result = call_model(task, api_key, max_tokens)
    result |= {"skill": task.skill, "scenario": task.scenario, "arm": task.arm,
               "rep": task.rep, "skill_md_sha": hashlib.sha256(task.system.encode()).hexdigest()[:12]}
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(result, indent=2))
    return task, result, False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills", help="comma-separated skill names (default: all)")
    parser.add_argument("--scenarios", type=int, help="use only the first N scenarios per skill")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--reps", type=int, default=1, help="samples per scenario and arm")
    parser.add_argument("--arm", choices=["with_skill", "without_skill", "both"], default="both")
    parser.add_argument("--skill-ref", help="read SKILL.md as of this git ref (default: working tree)")
    parser.add_argument("--web-search", type=int, default=0, metavar="N",
                        help="give the model N Exa search results via OpenRouter (about $0.004 per result)")
    parser.add_argument("--dry-run", action="store_true", help="plan only, no API calls")
    args = parser.parse_args()

    skills = [s.strip() for s in args.skills.split(",")] if args.skills else None
    arms = ("without_skill", "with_skill") if args.arm == "both" else (args.arm,)
    tasks = build_tasks(skills, args.scenarios, args.model, args.reps, arms, args.skill_ref,
                        args.web_search)
    if not tasks:
        sys.exit("no tasks matched")

    pending = [t for t in tasks if not (CACHE_DIR / f"{t.key}.json").is_file()]
    cached_count = len(tasks) - len(pending)

    print(f"model    : {args.model}")
    print(f"tasks    : {len(tasks)}  ({cached_count} cached, {len(pending)} to generate)")
    print(f"workers  : {args.workers}\n")

    if args.dry_run:
        for task in tasks:
            state = "CACHED" if (CACHE_DIR / f"{task.key}.json").is_file() else "run   "
            print(f"  [{state}] {task.label}  key={task.key}")
        return 0

    api_key = load_env().get("OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("OPENROUTER_API_KEY not found in eval-framework/.env")

    started = time.time()
    results: list[dict] = []
    fresh_cost = 0.0  # cached results carry their original cost; do not re-count it
    failures: list[str] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(run, t, api_key, args.max_tokens): t for t in tasks}
        for done, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            task = futures[future]
            try:
                _, result, was_cached = future.result()
            except Exception as exc:  # noqa: BLE001 - one failure must not sink the sweep
                failures.append(f"{task.label}: {exc}")
                print(f"  [{done}/{len(tasks)}] FAILED  {task.label}\n      {exc}")
                continue

            results.append(result)
            if not was_cached:
                fresh_cost += result.get("cost_usd") or 0
            if was_cached:
                print(f"  [{done}/{len(tasks)}] cached  {task.label}")
            else:
                print(
                    f"  [{done}/{len(tasks)}] done    {task.label}  "
                    f"{result['elapsed_seconds']:.0f}s  "
                    f"{len(result['output'].splitlines())} lines  "
                    f"${result['cost_usd']:.4f}"
                )

    # Write a run manifest so a later analysis pass can find these exact generations.
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime(started))
    spent = fresh_cost
    manifest = {
        "run_id": run_id,
        "model_requested": args.model,
        "web_search": args.web_search,
        "served_models": sorted({r.get("served_model") for r in results if r.get("served_model")}),
        "task_count": len(tasks),
        "generated": len(pending) - len(failures),
        "failures": failures,
        "total_cost_usd": round(spent, 4),
        "wall_clock_seconds": round(time.time() - started, 1),
        "tasks": [
            {"skill": t.skill, "scenario": t.scenario, "arm": t.arm, "rep": t.rep, "key": t.key}
            for t in tasks
        ],
    }
    (RUNS_DIR / f"{run_id}.json").write_text(json.dumps(manifest, indent=2))

    print(f"\nrun {run_id}")
    print(f"  cost       ${spent:.4f} (this invocation; cached tasks cost nothing)")
    print(f"  wall clock {manifest['wall_clock_seconds']:.0f}s")
    print(f"  manifest   {(RUNS_DIR / f'{run_id}.json').relative_to(REPO)}")
    if failures:
        print(f"  FAILURES   {len(failures)}")
        for line in failures:
            print(f"    - {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
