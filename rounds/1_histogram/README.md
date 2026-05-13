# Round 1 — Byte-pair histogram

## Problem

Given a binary payload of up to a few hundred megabytes, count the frequency of
every **2-byte bigram**. The output is a mapping from each observed bigram to
its occurrence count.

- Input: `data/payload.bin` (default 20 MB, biased byte distribution)
- Output: `dict` (or equivalent) keyed by 2-byte token → integer count
- Universe: up to 65,536 distinct bigrams

## What "fast" means here

Primarily **memory footprint** and **end-to-end wall time**. The naive approach
allocates an enormous number of tiny `bytes` objects — those allocations are
exactly the cost you want to drive down.

## Files

| File | Purpose |
|---|---|
| `baseline.py` | The intentionally slow starting point. **Don't edit** — it's the reference for the comparison. |
| `solution.py` | **Edit this.** Starts out delegating to `baseline.py`; replace with your faster implementation. |
| `gen_data.py` | Generates `data/payload.bin` and `data/fixture/payload.bin`. |
| `test_histogram.py` | Correctness tests + pytest-codspeed benchmark. Every test is parametrized to run against both the baseline and your solution. |

## Generate the data

```bash
python rounds/1_histogram/gen_data.py            # default 20 MB
python rounds/1_histogram/gen_data.py --size-mb 50
```

(Or run `python scripts/setup.py` to generate every round's data at once.)

## Verify correctness

```bash
uv run pytest rounds/1_histogram/
```

## Benchmark

```bash
uv run pytest --codspeed rounds/1_histogram/
```

CodSpeed CLI (instrumented):

```bash
codspeed run uv run pytest --codspeed rounds/1_histogram/
```

## Toolbox for this round

You don't need all of these — pick a few and measure.

- Stay in `bytes` end-to-end; skip the text-mode round-trip.
- `memoryview` over the buffer to avoid slice allocations.
- Represent each bigram as an `int` (`(b0 << 8) | b1`) and count into a
  preallocated `array('I')` (or `list`) of length 65,536.
- Stream with `readinto()` into a reusable `bytearray` to keep peak memory flat.
- Convert back to `dict[bytes, int]` only at the very end (or change the API).
