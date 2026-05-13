# Round 2 — Corruption scanner

## Problem

Given two equally-sized binary files — a known-good `reference.bin` and a
possibly damaged `corrupted.bin` — find **every byte range** where they differ
and return them as a list of `(offset, length)` tuples. Adjacent differing
bytes must be merged into a single range.

- Input: `data/reference.bin` and `data/corrupted.bin` (default 128 MB each;
  scale up to 2 GB via `--size-mb 2048` as a stretch goal)
- Output: `list[tuple[int, int]]` sorted by offset, no overlaps

## What "fast" means here

**End-to-end wall time** under tight **memory** constraints. The naive
"slurp both files into memory then loop byte-by-byte" approach pegs both peak
RSS and the Python interpreter. The fastest implementations stream chunks and
do the actual comparison in C (NumPy, `bytes` equality, etc.).

## Files

| File | Purpose |
|---|---|
| `baseline.py` | The intentionally slow starting point. **Don't edit** — it's the reference for the comparison. |
| `solution.py` | **Edit this.** Starts out delegating to `baseline.py`; replace with your faster implementation. |
| `gen_data.py` | Generates the reference + corrupted pair plus a `truth.json`. |
| `test_corruption.py` | Correctness tests + pytest-codspeed benchmark. Every test is parametrized to run against both the baseline and your solution. |

## Generate the data

```bash
python rounds/2_corruption/gen_data.py                 # default 128 MB
python rounds/2_corruption/gen_data.py --size-mb 2048  # 2 GB stretch goal
```

## Verify correctness

```bash
uv run pytest rounds/2_corruption/
```

## Benchmark

```bash
uv run pytest --codspeed rounds/2_corruption/
```

## Toolbox for this round

- Chunked streaming with `readinto()` into a reusable `bytearray` (keeps peak
  memory flat regardless of file size).
- `memoryview` to compare chunks without slicing.
- NumPy: view each chunk as `np.uint8`, compute `diff = a != b`, then turn
  the index array into `(offset, length)` ranges via `np.diff` / boundary
  detection.
- Async I/O pipelining: overlap disk reads with compare work using a small
  queue of chunks.
- Free-threaded CPython: split the file into chunks, scan them in parallel,
  then fix up boundary ranges in a final merge step.
