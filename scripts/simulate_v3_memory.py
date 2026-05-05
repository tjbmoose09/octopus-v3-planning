#!/usr/bin/env python3
"""Synthetic Octopus V3 memory/data-plane simulation.

This is intentionally dependency-free. It compares a V2-style broad context
loader against the proposed OctoSparse compiler over the local Octopus V2 repo
corpus. It does not measure LLM inference speed.
"""

from __future__ import annotations

import json
import math
import re
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
V2_ROOT = ROOT.parent
if not (V2_ROOT / "PAPER.md").exists() and not (V2_ROOT / "config").exists():
    V2_ROOT = ROOT
RESULTS_DIR = ROOT / "results"
RESULTS_JSON = RESULTS_DIR / "v3_memory_simulation_results.json"
RESULTS_JSONL = RESULTS_DIR / "v3_memory_simulation_runs.jsonl"
RESULTS_MD = ROOT / "docs" / "SIMULATION_RESULTS.md"

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_./:-]{2,}")
SECRET_RE = re.compile(
    r"sk-ant-api03-[A-Za-z0-9_-]{15,}|"
    r"ghp_[A-Za-z0-9_]{20,}|"
    r"github_pat_[A-Za-z0-9_]{40,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"-----BEGIN (RSA |OPENSSH |EC |DSA |)?PRIVATE KEY-----"
)


TASKS = [
    {
        "name": "zone bridge routing",
        "query": "How does the hacker zone bridge prevent cross-zone routing and what API should show a 403?",
        "gold": {"zone", "bridge", "can_route", "session", "403", "hacker"},
    },
    {
        "name": "obsidian memory fallback",
        "query": "Find the plan for Obsidian memory fallback when the local REST API is offline.",
        "gold": {"obsidian", "memory", "fallback", "journal", "offline", "rest"},
    },
    {
        "name": "benchmark quality stub",
        "query": "Why is the benchmark quality score not trustworthy yet and what should V3 improve?",
        "gold": {"benchmark", "quality", "score", "stub", "evaluator", "harness"},
    },
    {
        "name": "mcp server routing",
        "query": "Summarize how MCP servers are registered and routed to agents.",
        "gold": {"mcp", "servers", "routing", "allowlist", "agents", "orchestrator"},
    },
    {
        "name": "frontend surface row",
        "query": "What does the frontend surface row represent and how should V3 make it authoritative?",
        "gold": {"surface", "frontend", "desktop", "terminal", "web", "extension"},
    },
    {
        "name": "secret leak prevention",
        "query": "What repo files and key patterns should be blocked before public release?",
        "gold": {"secret", ".env", "token", "github", "api", "gitignore"},
    },
    {
        "name": "skills registry",
        "query": "Describe the skill registry and how autonomous skills are distributed by role.",
        "gold": {"skills", "autonomous", "role", "registry", "agent", "config"},
    },
    {
        "name": "pipeline observability",
        "query": "Which persisted events power the live pipeline and mesh UI observability?",
        "gold": {"pipeline", "events", "websocket", "mesh", "log", "task"},
    },
]


@dataclass
class Chunk:
    id: int
    path: str
    text: str
    terms: Counter[str]
    token_count: int
    risk: float


def tokenize(text: str) -> list[str]:
    return [m.group(0).lower() for m in TOKEN_RE.finditer(text)]


def iter_source_files() -> list[Path]:
    include_roots = [
        "PAPER.md",
        "README.md",
        "ROADMAP_ISSUES.md",
        "ANNOUNCEMENT.md",
        "docs",
        "results",
        "config",
        "agents",
        "api",
        "benchmark",
        "tests",
    ]
    files: list[Path] = []
    for item in include_roots:
        path = V2_ROOT / item
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.suffix.lower() in {".md", ".py", ".sql", ".jsx", ".js", ".css"}:
                    files.append(child)
    return sorted(files)


def chunk_text(path: Path, chunk_words: int = 140) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_words):
        part = " ".join(words[i : i + chunk_words])
        if len(part.strip()) > 80:
            chunks.append(part)
    return chunks


def build_corpus() -> tuple[list[Chunk], dict[str, float], dict[str, list[int]], float]:
    start = time.perf_counter()
    chunks: list[Chunk] = []
    doc_freq: Counter[str] = Counter()
    inverted: defaultdict[str, list[int]] = defaultdict(list)
    source_files = iter_source_files()

    for path in source_files:
        rel = path.relative_to(V2_ROOT).as_posix()
        for text in chunk_text(path):
            terms = Counter(tokenize(text))
            if not terms:
                continue
            risk = 1.0 if SECRET_RE.search(text) else 0.0
            chunk = Chunk(len(chunks), rel, text, terms, sum(terms.values()), risk)
            chunks.append(chunk)
            doc_freq.update(terms.keys())
            for term in terms:
                inverted[term].append(chunk.id)

    idf = {
        term: math.log((len(chunks) + 1) / (freq + 1)) + 1.0
        for term, freq in doc_freq.items()
    }
    compile_ms = (time.perf_counter() - start) * 1000
    return chunks, idf, dict(inverted), compile_ms


def score(query_terms: Counter[str], chunk: Chunk, idf: dict[str, float]) -> float:
    score_value = 0.0
    for term, q_count in query_terms.items():
        if term in chunk.terms:
            score_value += q_count * chunk.terms[term] * idf.get(term, 1.0)
    return score_value


def precision(gold: set[str], selected: list[Chunk]) -> float:
    if not gold:
        return 0.0
    text = " ".join(chunk.text.lower() for chunk in selected)
    hits = sum(1 for term in gold if term.lower() in text)
    return hits / len(gold)


def v2_broad_loader(task: dict, chunks: list[Chunk], idf: dict[str, float]) -> dict:
    start = time.perf_counter()
    query_terms = Counter(tokenize(task["query"]))
    ranked = sorted(
        ((score(query_terms, chunk, idf), chunk) for chunk in chunks),
        key=lambda item: item[0],
        reverse=True,
    )
    # Simulate broad V2/V2.3-style context: load the top 24 chunks after a full scan.
    selected = [chunk for value, chunk in ranked[:24] if value > 0]
    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "latency_ms": elapsed_ms,
        "active_tokens": sum(chunk.token_count for chunk in selected),
        "precision": precision(set(task["gold"]), selected),
        "selected_count": len(selected),
        "risk_hits": sum(chunk.risk for chunk in selected),
        "paths": sorted({chunk.path for chunk in selected})[:10],
    }


def v3_sparse_compiler(
    task: dict,
    chunks: list[Chunk],
    idf: dict[str, float],
    inverted: dict[str, list[int]],
) -> dict:
    start = time.perf_counter()
    query_terms = Counter(tokenize(task["query"]))
    candidates = []
    candidate_ids: set[int] = set()
    for term in query_terms:
        candidate_ids.update(inverted.get(term, []))

    for chunk_id in candidate_ids:
        chunk = chunks[chunk_id]
        relevance = score(query_terms, chunk, idf)
        if relevance <= 0:
            continue
        novelty = len(set(query_terms) & set(chunk.terms)) / max(len(query_terms), 1)
        token_penalty = chunk.token_count / 450.0
        risk_penalty = 100.0 * chunk.risk
        utility = relevance + (2.0 * novelty) - token_penalty - risk_penalty
        candidates.append((utility, relevance, chunk))

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    active: list[Chunk] = []
    covered: set[str] = set()
    budget = 1150

    for _utility, _relevance, chunk in candidates:
        if sum(item.token_count for item in active) + chunk.token_count > budget:
            continue
        # DICG-inspired sparse active set: prefer atoms adding new query terms.
        contribution = set(query_terms) & set(chunk.terms)
        if contribution - covered or len(active) < 3:
            active.append(chunk)
            covered.update(contribution)
        if len(active) >= 8 or covered >= set(query_terms):
            break

    # Away-step cleanup: remove the most redundant chunk if budget is still dense.
    if len(active) > 5:
        term_coverage: defaultdict[str, int] = defaultdict(int)
        for chunk in active:
            for term in set(query_terms) & set(chunk.terms):
                term_coverage[term] += 1
        removable = []
        for chunk in active:
            unique_terms = [
                term for term in set(query_terms) & set(chunk.terms)
                if term_coverage[term] == 1
            ]
            removable.append((len(unique_terms), -chunk.token_count, chunk))
        removable.sort()
        if removable and removable[0][0] == 0:
            active.remove(removable[0][2])

    elapsed_ms = (time.perf_counter() - start) * 1000
    return {
        "latency_ms": elapsed_ms,
        "active_tokens": sum(chunk.token_count for chunk in active),
        "precision": precision(set(task["gold"]), active),
        "selected_count": len(active),
        "risk_hits": sum(chunk.risk for chunk in active),
        "paths": sorted({chunk.path for chunk in active})[:10],
    }


def aggregate(rows: list[dict]) -> dict:
    def avg(key: str) -> float:
        return statistics.fmean(row[key] for row in rows)

    def med(key: str) -> float:
        return statistics.median(row[key] for row in rows)

    return {
        "mean_latency_ms": avg("latency_ms"),
        "median_latency_ms": med("latency_ms"),
        "mean_active_tokens": avg("active_tokens"),
        "median_active_tokens": med("active_tokens"),
        "mean_precision": avg("precision"),
        "median_precision": med("precision"),
        "mean_selected_count": avg("selected_count"),
        "risk_hits": sum(row["risk_hits"] for row in rows),
    }


def pct_change(old: float, new: float, lower_is_better: bool) -> float:
    if old == 0:
        return 0.0
    raw = (old - new) / old if lower_is_better else (new - old) / old
    return raw * 100


def signed_change(value: float, positive_label: str, negative_label: str) -> str:
    if value >= 0:
        return f"{value:.1f}% {positive_label}"
    return f"{abs(value):.1f}% {negative_label}"


def write_markdown(result: dict) -> None:
    v2 = result["aggregate"]["v2_baseline"]
    v3 = result["aggregate"]["v3_sparse"]
    token_drop = pct_change(v2["mean_active_tokens"], v3["mean_active_tokens"], True)
    latency_drop = pct_change(v2["mean_latency_ms"], v3["mean_latency_ms"], True)
    precision_gain = pct_change(v2["mean_precision"], v3["mean_precision"], False)
    prompt_eval_rate = 75.0
    v2_prompt_ms = (v2["mean_active_tokens"] / prompt_eval_rate) * 1000
    v3_prompt_ms = (v3["mean_active_tokens"] / prompt_eval_rate) * 1000
    prompt_ms_drop = pct_change(v2_prompt_ms, v3_prompt_ms, True)
    v2_total_ms = v2_prompt_ms + v2["mean_latency_ms"]
    v3_total_ms = v3_prompt_ms + v3["mean_latency_ms"]
    estimated_total_drop = pct_change(v2_total_ms, v3_total_ms, True)

    lines = [
        "# V3 Memory/Data-Plane Simulation Results",
        "",
        f"Run date: {result['run_date']}",
        "",
        "## What Was Simulated",
        "",
        "This is a deterministic simulation of the proposed V3 memory compiler over the available Octopus V2 repo corpus. It compares:",
        "",
        "- `v2_baseline`: broad V2/V2.3-style retrieval that scans the corpus and loads a larger context bundle.",
        "- `v3_sparse`: OctoSparse-style active-set retrieval with token budget, novelty scoring, away-step cleanup, and secret-risk penalty.",
        "",
        "This does not measure real LLM inference, model quality, GPU throughput, or production latency. It measures data-plane behavior: retrieval time, active context size, synthetic precision, and leak-risk selection.",
        "",
        "No V2.3-specific paper was present in the local repo at simulation time, so the baseline uses the available V2.2 paper/docs and the current V2 code corpus as the V2.x reference.",
        "",
        "## Aggregate Result",
        "",
        "| Metric | V2.x broad baseline | V3 sparse compiler | Simulated change |",
        "|---|---:|---:|---:|",
        f"| Mean retrieval latency | {v2['mean_latency_ms']:.3f} ms | {v3['mean_latency_ms']:.3f} ms | {signed_change(latency_drop, 'faster', 'slower')} |",
        f"| Median retrieval latency | {v2['median_latency_ms']:.3f} ms | {v3['median_latency_ms']:.3f} ms | {signed_change(pct_change(v2['median_latency_ms'], v3['median_latency_ms'], True), 'faster', 'slower')} |",
        f"| Mean active context | {v2['mean_active_tokens']:.1f} tokens | {v3['mean_active_tokens']:.1f} tokens | {token_drop:.1f}% fewer tokens |",
        f"| Median active context | {v2['median_active_tokens']:.1f} tokens | {v3['median_active_tokens']:.1f} tokens | {pct_change(v2['median_active_tokens'], v3['median_active_tokens'], True):.1f}% fewer tokens |",
        f"| Mean synthetic precision | {v2['mean_precision']:.3f} | {v3['mean_precision']:.3f} | {signed_change(precision_gain, 'relative gain', 'relative drop')} |",
        f"| Mean selected chunks | {v2['mean_selected_count']:.1f} | {v3['mean_selected_count']:.1f} | {pct_change(v2['mean_selected_count'], v3['mean_selected_count'], True):.1f}% smaller active set |",
        f"| Estimated prompt eval @ {prompt_eval_rate:.0f} tok/s | {v2_prompt_ms / 1000:.2f} s | {v3_prompt_ms / 1000:.2f} s | {prompt_ms_drop:.1f}% faster |",
        f"| Estimated retrieval + prompt eval | {v2_total_ms / 1000:.2f} s | {v3_total_ms / 1000:.2f} s | {estimated_total_drop:.1f}% faster |",
        f"| Selected secret-risk hits | {v2['risk_hits']:.0f} | {v3['risk_hits']:.0f} | risk selections avoided |",
        "",
        "## Interpretation",
        "",
        f"In this simulation, the V3 sparse compiler reduced active context by **{token_drop:.1f}%**. Mean synthetic precision moved from **{v2['mean_precision']:.3f}** to **{v3['mean_precision']:.3f}**, a **{abs(precision_gain):.1f}% relative {'gain' if precision_gain >= 0 else 'drop'}**. Raw retrieval bookkeeping was slower in this tiny Python prototype, but the estimated downstream prompt-evaluation cost fell by **{prompt_ms_drop:.1f}%** because the model would receive far fewer context tokens.",
        "",
        f"The important V3 signal is that a sparse active set preserved most task-relevant coverage while loading far less context. At an illustrative local prompt-eval rate of {prompt_eval_rate:.0f} tokens/sec, the estimated retrieval-plus-prompt stage improves by **{estimated_total_drop:.1f}%**. This is the performance increase to validate with real model replay.",
        "",
        "## Per-Task Results",
        "",
        "| Task | V2 tokens | V3 tokens | Token drop | V2 precision | V3 precision |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for row in result["tasks"]:
        v2r = row["v2_baseline"]
        v3r = row["v3_sparse"]
        lines.append(
            f"| {row['name']} | {v2r['active_tokens']} | {v3r['active_tokens']} | "
            f"{pct_change(v2r['active_tokens'], v3r['active_tokens'], True):.1f}% | "
            f"{v2r['precision']:.3f} | {v3r['precision']:.3f} |"
        )

    lines += [
        "",
        "## Recommendation",
        "",
        "Promote OctoSparse DICG into the V3 prototype harness as the first serious candidate. The next step is to replace the synthetic precision metric with evaluator-graded answers from local models and replay real long-running Octopus sessions.",
        "",
        "## Guardrails",
        "",
        "- Do not claim these numbers as production model-speed gains.",
        "- Treat them as data-plane simulation gains over the available V2.x corpus.",
        "- Require live LLM replay before publishing performance claims externally.",
        "- Add a V2.3-specific baseline if/when a V2.3 paper or branch exists.",
        "",
    ]

    RESULTS_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    chunks, idf, inverted, compile_ms = build_corpus()
    started = time.perf_counter()
    task_rows = []

    for task in TASKS:
        v2 = v2_broad_loader(task, chunks, idf)
        v3 = v3_sparse_compiler(task, chunks, idf, inverted)
        task_rows.append({
            "name": task["name"],
            "query": task["query"],
            "gold": sorted(task["gold"]),
            "v2_baseline": v2,
            "v3_sparse": v3,
        })

    result = {
        "run_date": time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "corpus": {
            "root": str(V2_ROOT),
            "chunk_count": len(chunks),
            "source_file_count": len(iter_source_files()),
            "idf_terms": len(idf),
            "index_compile_ms": compile_ms,
        },
        "task_count": len(TASKS),
        "elapsed_ms": (time.perf_counter() - started) * 1000,
        "aggregate": {
            "v2_baseline": aggregate([row["v2_baseline"] for row in task_rows]),
            "v3_sparse": aggregate([row["v3_sparse"] for row in task_rows]),
        },
        "tasks": task_rows,
    }

    RESULTS_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for row in task_rows:
            handle.write(json.dumps(row) + "\n")
    write_markdown(result)
    print(json.dumps(result["aggregate"], indent=2))
    print(f"Wrote {RESULTS_JSON.relative_to(ROOT)}")
    print(f"Wrote {RESULTS_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
