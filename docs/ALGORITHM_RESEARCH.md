# Algorithm Research Notes

## Source: Decomposition-Invariant Conditional Gradient

Paper: "Linear-Memory and Decomposition-Invariant Linearly Convergent Conditional Gradient Algorithm for Structured Polytopes" by Dan Garber and Ofer Meshi, NeurIPS 2016.

Key takeaways:

- The paper targets conditional-gradient / Frank-Wolfe optimization over structured polytopes.
- Its main complaint about prior away-step methods is that they maintain an explicit convex decomposition of the current iterate, causing high memory and runtime overhead.
- The proposed DICG method computes away steps without depending on a stored decomposition.
- The paper reports linear memory and computation overhead in the dimension, with better convergence dependence when the optimum is sparse.
- The guarantee applies to structured polytopes, not every possible domain.

V3 interpretation:

- Treat the active context as a sparse feasible point, not as a full transcript decomposition.
- Retrieve "toward" atoms that best reduce task error.
- Evict or downweight "away" atoms without storing every historical decomposition that produced the current context.
- Reward sparse solutions: the best answer should need the fewest high-value memory atoms.

## Reviewer Notes That Matter

The NeurIPS reviews mostly liked the contribution but flagged implementation and scope risks:

- The algorithm is strong where the structure assumptions hold.
- Reviewers wanted more clarity on when decomposition-invariance gives practical benefit.
- Some reviewers questioned claims about competing methods' quadratic costs in common implementations.
- Experiments needed fuller detail.

V3 implication:

- Do not claim universal superiority.
- Build a harness that makes structure assumptions explicit.
- Report wins and losses per data shape.

## SVDD

Support Vector Data Description is a one-class boundary method: it describes "normal" data with a compact boundary and flags items outside it as novelty/outliers.

V3 uses:

- detect abnormal memory writes
- detect repo leak risk before publishing
- detect prompt/tool-output drift from expected project domain
- flag low-confidence retrievals outside the known project boundary

Fast iterative SVDD variants are interesting because classic SVDD can be expensive. V3 should start with a lightweight approximation:

- embeddings for memory atoms
- rolling centroid/radius per scope
- support-vector-like boundary examples
- periodic recalibration from accepted atoms

## Loop Nesting / Data Layout

Loop nesting optimization is about making repeated computation cache-friendly by choosing loop order, tiling, and data layout together.

V3 uses:

- batch embeddings by source and model
- tile memory scans by scope, recency, and vector shard
- avoid repeatedly walking the same data for each agent
- compile daily memory journals in cache-friendly passes

This is an engineering layer, not an agent-brain concept.

## SDARP

SDARP can mean different things in the literature. Two relevant meanings surfaced:

- Security based Data Aware Routing Protocol for ad hoc sensor networks.
- Selective Dial-A-Ride Problem algorithms using fragments and decomposition.

For Octopus V3, the sensor-routing interpretation is more useful:

- route data based on security/risk score, freshness, cost, and utility
- prefer local low-risk lanes by default
- escalate to higher-cost or cloud lanes only with policy reasons

The dial-a-ride interpretation is useful as a metaphor for scheduling:

- memory atoms are pickups
- agent context windows are vehicles
- context budget is capacity
- each atom has time/priority constraints

## Asif's Algorithm

"Asif's Algorithm" is ambiguous. Search results point to several unrelated Asif-authored compression or data-processing papers, including urban traffic data compression, DCT/WPT compression, point-cloud compression, and article summaries by Asif Razzaq.

V3 should not assume a single canonical "Asif algorithm" until the exact paper or DOI is identified.

Provisional test bucket:

- DCT-selected coefficient compression
- wavelet packet compression
- traffic/time-series delta compression
- point-cloud polynomial approximation if V3 starts handling spatial/multimodal memory

