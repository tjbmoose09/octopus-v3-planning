# V3 Memory/Data-Plane Simulation Results

Run date: 2026-05-04 21:31:16 Eastern Daylight Time

## What Was Simulated

This is a deterministic simulation of the proposed V3 memory compiler over the available Octopus V2 repo corpus. It compares:

- `v2_baseline`: broad V2/V2.3-style retrieval that scans the corpus and loads a larger context bundle.
- `v3_sparse`: OctoSparse-style active-set retrieval with token budget, novelty scoring, away-step cleanup, and secret-risk penalty.

This does not measure real LLM inference, model quality, GPU throughput, or production latency. It measures data-plane behavior: retrieval time, active context size, synthetic precision, and leak-risk selection.

No V2.3-specific paper was present in the local repo at simulation time, so the baseline uses the available V2.2 paper/docs and the current V2 code corpus as the V2.x reference.

LM Studio was not reachable at `localhost:1234` during this run, so no live local-model replay was performed.

## Aggregate Result

| Metric | V2.x broad baseline | V3 sparse compiler | Simulated change |
|---|---:|---:|---:|
| Mean retrieval latency | 0.358 ms | 1.636 ms | 356.9% slower |
| Median retrieval latency | 0.328 ms | 1.483 ms | 351.9% slower |
| Mean active context | 2717.1 tokens | 545.8 tokens | 79.9% fewer tokens |
| Median active context | 2642.5 tokens | 535.5 tokens | 79.7% fewer tokens |
| Mean synthetic precision | 0.958 | 0.938 | 2.2% relative drop |
| Mean selected chunks | 24.0 | 5.1 | 78.6% smaller active set |
| Estimated prompt eval @ 75 tok/s | 36.23 s | 7.28 s | 79.9% faster |
| Estimated retrieval + prompt eval | 36.23 s | 7.28 s | 79.9% faster |
| Selected secret-risk hits | 0 | 0 | risk selections avoided |

## Interpretation

In this simulation, the V3 sparse compiler reduced active context by **79.9%**. Mean synthetic precision moved from **0.958** to **0.938**, a **2.2% relative drop**. Raw retrieval bookkeeping was slower in this tiny Python prototype, but the estimated downstream prompt-evaluation cost fell by **79.9%** because the model would receive far fewer context tokens.

The important V3 signal is that a sparse active set preserved most task-relevant coverage while loading far less context. At an illustrative local prompt-eval rate of 75 tokens/sec, the estimated retrieval-plus-prompt stage improves by **79.9%**. This is the performance increase to validate with real model replay.

## Per-Task Results

| Task | V2 tokens | V3 tokens | Token drop | V2 precision | V3 precision |
|---|---:|---:|---:|---:|---:|
| zone bridge routing | 2651 | 563 | 78.8% | 1.000 | 1.000 |
| obsidian memory fallback | 2627 | 547 | 79.2% | 1.000 | 1.000 |
| benchmark quality stub | 2611 | 467 | 82.1% | 1.000 | 1.000 |
| mcp server routing | 2915 | 476 | 83.7% | 1.000 | 1.000 |
| frontend surface row | 2720 | 562 | 79.3% | 1.000 | 1.000 |
| secret leak prevention | 2963 | 719 | 75.7% | 0.667 | 0.500 |
| skills registry | 2616 | 508 | 80.6% | 1.000 | 1.000 |
| pipeline observability | 2634 | 524 | 80.1% | 1.000 | 1.000 |

## Recommendation

Promote OctoSparse DICG into the V3 prototype harness as the first serious candidate. The next step is to replace the synthetic precision metric with evaluator-graded answers from local models and replay real long-running Octopus sessions.

## Guardrails

- Do not claim these numbers as production model-speed gains.
- Treat them as data-plane simulation gains over the available V2.x corpus.
- Require live LLM replay before publishing performance claims externally.
- Add a V2.3-specific baseline if/when a V2.3 paper or branch exists.
