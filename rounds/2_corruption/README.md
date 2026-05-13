# Round 2 — Corruption scanner

## Problem

Given two equally-sized binary files — a known-good `reference.bin` and a
possibly damaged `corrupted.bin` — find **every byte range** where they differ
and return them as a list of `(offset, length)` tuples. Adjacent differing
bytes must be merged into a single range.

- Input: `data/reference.bin` and `data/corrupted.bin` (default 64 MB each;
  scale up to 1 GB via `--size-mb 1024` as a stretch goal)
- Output: `list[tuple[int, int]]` sorted by offset, no overlaps

## What "fast" means here

**End-to-end wall time** under tight **memory** constraints. The naive
"slurp both files into memory then loop byte-by-byte" approach pegs both peak
RSS and the Python interpreter. The fastest implementations stream chunks and
do the actual comparison in C (NumPy, `bytes` equality, etc.).

## Files

| File                 | Purpose                                                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `baseline.py`        | The intentionally slow starting point. **Don't edit** — it's the reference for the comparison.                                |
| `solution.py`        | **Edit this.** Starts out delegating to `baseline.py`; replace with your faster implementation.                               |
| `gen_data.py`        | Generates the reference + corrupted pair plus a `truth.json`.                                                                 |
| `test_corruption.py` | Correctness tests + pytest-codspeed benchmark. Every test is parametrized to run against both the baseline and your solution. |

## Generate the data

```bash
uv run rounds/2_corruption/gen_data.py                 # default 64 MB
uv run rounds/2_corruption/gen_data.py --size-mb 1024  # 1 GB stretch goal
```

## Verify correctness

```bash
uv run pytest rounds/2_corruption/
```

## Benchmark

```bash
uv run pytest --codspeed rounds/2_corruption/
```

```bash
codspeed run --mode walltime -- uv run pytest --codspeed rounds/2_corruption/
```
