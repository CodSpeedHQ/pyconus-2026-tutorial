# Round 1: Byte-pair histogram

## Problem

Given a binary payload of up to a few hundred megabytes, count the frequency
of every **2-byte bigram**. The output is a mapping from each observed bigram
to its occurrence count.

A **bigram** is a sliding window of two adjacent bytes. For the payload
`b"ABCD"` the bigrams are `b"AB"`, `b"BC"`, and `b"CD"`. An `N`-byte payload
therefore contains `N - 1` bigrams. With 256 possible byte values each, the
full universe is `256 * 256 = 65,536` distinct tokens.

- Input: `data/payload.bin` (default 10 MB, biased byte distribution).
- Output: a `dict` (or equivalent) keyed by 2-byte token, mapped to an `int` count.
- Universe: up to 65,536 distinct bigrams.

## Files

| File                | Purpose                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `baseline.py`       | Intentionally slow starting point. **Don't edit:** it is the reference for the comparison.                                |
| `solution.py`       | **Edit this.** Starts out delegating to `baseline.py`; replace with your faster implementation.                           |
| `gen_data.py`       | Generates `data/payload.bin` and `data/fixture/payload.bin`.                                                              |
| `test_histogram.py` | Correctness tests and the pytest-codspeed benchmark. Every test is parametrized over both the baseline and your solution. |

## Generate the data

```bash
uv run rounds/1_histogram/gen_data.py            # default 10 MB.
uv run rounds/1_histogram/gen_data.py --size-mb 50
```

Or run `uv run scripts/setup.py` to generate every round's data in
one go.

## Verify correctness

```bash
uv run pytest rounds/1_histogram/
```

## Benchmark

Walltime, locally:

```bash
uv run pytest --codspeed rounds/1_histogram/
```

Same benchmarks, run through the CodSpeed CLI for low-noise instrumented
measurements:

```bash
codspeed run --mode walltime -- uv run pytest --codspeed rounds/1_histogram/
```
