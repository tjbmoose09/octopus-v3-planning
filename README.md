# Octopus V3 Planning

Private planning repo for Octopus V3: faster memory, smarter data compilation/decompilation, stronger benchmark discipline, and a new algorithm family inspired by decomposition-invariant conditional gradient methods.

## V3 Thesis

Octopus V2.2 proved that a local-first multi-agent mesh can run on one workstation. V3 should make the mesh faster and more reliable by changing how information moves:

- compile raw conversation/tool data into sparse, typed memory atoms
- decompile memory atoms back into task-ready context only when needed
- recompile stale or redundant memory into smaller summaries
- route data through risk-aware and density-aware lanes
- benchmark each algorithm against the current V2 baseline until one clearly wins

## Core Documents

- [V3 Scope](docs/V3_SCOPE.md)
- [Algorithm Research](docs/ALGORITHM_RESEARCH.md)
- [Stress Test Plan](docs/STRESS_TEST_PLAN.md)
- [Mind Map](docs/MIND_MAP.md)
- [Proposed Algorithm](docs/OCTOSPARSE_DICG_ALGORITHM.md)

## Initial Repo Status

This repo is a planning seed. Implementation should start only after the benchmark harness and evaluation metrics are accepted.

