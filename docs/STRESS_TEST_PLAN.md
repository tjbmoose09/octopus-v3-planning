# Stress Test Plan

## Purpose

Stress test candidate memory and data-processing algorithms against Octopus V2 until one is clearly better for V3.

## Baseline

V2 baseline:

- current SQLite task/message/pipeline tables
- current Obsidian memory path
- current retrieval/search behavior
- current summarization/compaction behavior
- current model routing latency

## Competitors

1. V2 baseline
2. Sparse active-set memory
3. DICG-inspired away-step eviction
4. SVDD-guarded memory admission
5. SDARP-style risk/utility routing
6. Loop-tiled batch compiler
7. Hybrid: sparse active set + SVDD guard + loop-tiled compiler
8. Proposed OctoSparse DICG compiler

## Data Sets

Synthetic:

- 10-turn, 100-turn, 1,000-turn project transcripts
- duplicate-heavy logs
- contradiction-heavy logs
- secret-contaminated logs
- high-tool-output logs

Real:

- Octopus V2 docs
- public repo issue/commit history
- anonymized local pipeline events
- benchmark outputs
- README/docs generation tasks

## Metrics

Speed:

- compile latency
- decompile latency
- retrieval latency
- end-to-end answer latency

Memory:

- RAM footprint
- database size
- index size
- active-context tokens

Quality:

- top-k retrieval precision
- source citation correctness
- answer correctness rubric
- contradiction handling
- long-task resume quality

Safety:

- secret detection recall
- false positive rate
- risky atom rejection rate
- provenance preservation

Decision rule:

An algorithm wins only if it improves speed and token footprint without hurting correctness or safety. If two are close, choose the simpler implementation.

## Tournament Rounds

Round 1: synthetic data sanity checks.

Round 2: replay V2 project history.

Round 3: adversarial leak and contradiction injection.

Round 4: long-running build simulation with forced compaction every 65 percent of context budget.

Round 5: live dogfooding in a private branch.

## Output

Each run emits:

- `results.jsonl`
- `summary.md`
- plots for latency, memory, precision, and safety
- recommendation: promote, hold, reject

