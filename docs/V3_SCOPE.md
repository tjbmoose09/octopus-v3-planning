# Octopus V3 Scope

## Goal

Build a faster, safer, more accurate Octopus runtime by replacing linear transcript accumulation with a sparse data compiler and an algorithm tournament.

V3 is not just "more agents." It is a data-plane upgrade.

## Workstreams

1. Memory compiler

- Convert events, chats, tool outputs, and docs into typed memory atoms.
- Store atoms with source, confidence, recency, risk, agent ownership, and retrieval affordances.
- Keep the active context sparse: only include atoms that matter for the current task.

2. Decompile/recompile layer

- Decompile compact atoms back into context blocks, plans, constraints, or citations.
- Recompile old atoms into tighter summaries when they become redundant.
- Preserve provenance so compression never destroys where a claim came from.

3. Algorithm tournament

- Stress test candidate methods against V2: current retrieval, summarization, memory writes, routing, and benchmark harness.
- Compare latency, token load, answer accuracy, memory footprint, hallucination rate, retrieval precision, and recovery after context compaction.
- Promote a method only if it wins on real tasks, not just synthetic metrics.

4. Safety/risk layer

- Add leak scanning and risk scores to every memory write and repo export.
- Add anomaly detection for memory atoms using SVDD-style boundaries.
- Prevent risky local state from crossing into GitHub, docs, or public release artifacts.

5. V3 UI and observability

- Show memory compilation/decompilation as first-class activity.
- Add charts for latency, memory footprint, compression ratio, and retrieval accuracy.
- Add a "why this context was loaded" explainer per answer.

## Candidate Concepts To Evaluate

- Decomposition-invariant conditional gradient ideas from Garber and Meshi's 2016 NeurIPS paper.
- Loop nesting and data-layout optimization for cache-aware batch processing.
- SVDD for novelty, anomaly, and risk detection around memory writes and repo exports.
- SDARP-style secure/data-aware routing adapted from sensor routing, not copied directly.
- Sparse active-set memory, vector quantization, delta encoding, and adaptive summarization.

## V3 Acceptance Criteria

V3 should beat V2 on:

- median response latency by at least 25 percent
- context token load by at least 40 percent on long projects
- retrieval precision at top 5 by at least 20 percent
- no increase in hallucination rate
- no secret/local-state leaks in generated docs or commits
- successful recovery from a 100-turn task after forced compaction

