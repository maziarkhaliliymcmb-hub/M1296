# M1296 — Directed Influence Graph

M1296 defines 36×36 = 1296 directed source→target slots, including self-loops. Reverse edges are independent. The graph is sparse and supports downstream impact traversal and strongly connected component analysis.

## Run
```bash
python -m pip install -r requirements.txt
python -m pip install -e .
pytest -q
```

Cycles require policy classification; a feedback loop is not automatically unsafe. See `M1296_SPEC.md`.

Change trace: CHG-20261124-M36-001 (canonical record in 36OS-database).
