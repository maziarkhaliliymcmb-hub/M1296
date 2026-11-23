# M1296 Directed Influence Graph 1.0.0

M1296 is a 36×36 directed address space: 1296 possible source→target positions, including 36 self-loops. The edge (i,j) is independent of (j,i); no symmetry is assumed.

The implementation is sparse: only declared edges consume storage. It supports directed impact traversal, inactive edges, and cycle inspection. A detected cycle is not automatically classified as unsafe: policy must distinguish permitted feedback loops from prohibited control/dependency cycles.

Weights and confidence are bounded metadata, not inferred truth. They must be populated from measured evidence, validated experiments, or approved rules. This package does not execute workflows or alter M36 root genes.
