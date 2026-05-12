# Round 2: Corruption scanner

## Problem

You have two equally-sized binary files: a known-good `reference.bin` and a
possibly damaged `corrupted.bin`.

Find **every byte range** where they differ
and return the ranges as a list of `(offset, length)` tuples. Adjacent
differing bytes must be merged into a single range.

- Input: `data/reference.bin` and `data/corrupted.bin` (default 64 MB each;
  scale up to 1 GB via `--size-mb 1024` as a stretch goal).
- Output: `list[tuple[int, int]]` sorted by offset, with no overlaps.

## Files

| File                 | Purpose                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `baseline.py`        | Intentionally slow starting point. **Don't edit:** it is the reference for the comparison.                                |
| `solution.py`        | **Edit this.** Starts out delegating to `baseline.py`; replace with your faster implementation.                           |
| `gen_data.py`        | Generates the reference and corrupted pair alongside a `truth.json`.                                                      |
| `test_corruption.py` | Correctness tests and the pytest-codspeed benchmark. Every test is parametrized over both the baseline and your solution. |

## Generate the data

```bash
uv run rounds/2_corruption/gen_data.py                 # default 64 MB.
uv run rounds/2_corruption/gen_data.py --size-mb 1024  # 1 GB stretch goal.
```

Or run `uv run scripts/setup.py` to generate every round's data in one go.

## Verify correctness

```bash
uv run pytest rounds/2_corruption/
```

## Benchmark

Walltime, locally:

```bash
uv run pytest --codspeed rounds/2_corruption/
```

```bash
codspeed run --mode walltime -- uv run pytest --codspeed rounds/2_corruption/
```
