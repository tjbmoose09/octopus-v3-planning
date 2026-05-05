# Proposed Algorithm: OctoSparse DICG Memory Compiler

## Summary

OctoSparse DICG is a V3 candidate algorithm for compiling, retrieving, and evicting memory. It adapts the useful idea from decomposition-invariant conditional gradient methods: improve the current active context without carrying the whole decomposition history that produced it.

It is not a literal implementation of the NeurIPS optimization paper. It is an Octopus-specific data-plane algorithm inspired by the same principle.

## Data Model

Each memory atom has:

- `id`
- `scope`
- `embedding`
- `summary`
- `source_ref`
- `timestamp`
- `confidence`
- `risk_score`
- `utility_score`
- `token_cost`
- `agent_owner`
- `supersedes`

The active context is a sparse weighted set of atoms:

```text
context = { atom_id -> weight }
```

## Core Loop

Input:

- task query
- current active context
- candidate atom index
- context token budget
- safety policy

Steps:

1. Compute a task-gradient proxy.

   Use retrieval loss, missing constraints, unanswered subgoals, and contradiction penalties as a practical gradient approximation.

2. Select a toward atom.

   Pick the candidate atom with highest positive utility:

   ```text
   toward_score = relevance + novelty + confidence - risk - token_cost
   ```

3. Select an away atom.

   Pick the current active atom with worst marginal contribution:

   ```text
   away_score = redundancy + contradiction + staleness + risk + token_cost - relevance
   ```

4. Update weights.

   Increase the toward atom and decrease the away atom. If the away atom weight reaches zero, evict it.

5. Guard with SVDD.

   Reject or quarantine atoms outside the normal boundary for the current scope unless explicitly approved.

6. Enforce budget.

   Continue until token budget is met and marginal utility flattens.

7. Decompile.

   Render active atoms into the smallest task-specific context block with citations and constraints.

## Why It Might Beat V2

V2 tends to accumulate transcripts, summaries, and route logs. OctoSparse DICG keeps an active support set.

Expected advantages:

- lower active token count
- faster retrieval after long histories
- better long-task resume quality
- explicit provenance
- safer public export path
- less dependence on a single summarization pass

## Failure Modes

- Bad gradient proxy can evict important context.
- Over-aggressive sparsity can remove nuance.
- SVDD can reject unusual but important new information.
- Scoring weights may overfit early dogfooding tasks.

## Required Stress Tests

- hidden dependency task: important fact appears only once early in history
- contradiction task: old and new project decisions conflict
- leak injection task: secret-looking strings enter logs
- repeated-noise task: huge repeated tool output
- branching task: multiple agents generate competing plans

## Promotion Rule

Promote only if it beats V2 baseline and hybrid competitors on:

- median latency
- p95 latency
- top-k retrieval precision
- active token count
- long-task resume score
- leak detection recall

