# Round 3 (final challenge): DNA sequence matcher

## Problem

Given a FASTA-like file (`genome.fasta`) containing DNA sequences using only
`A`, `C`, `G`, `T`, find **every record whose sequence contains a target
pattern** and return the positions of each occurrence inside that record.

A **FASTA** record starts with a `>` header line containing the record id,
followed by one or more lines of sequence data. The file packs many records
back-to-back:

```
>seq_000001
ACGTACGTACGT
ACGTACGTACGT
>seq_000002
TGCATGCATGCA
```

- Input: `data/genome.fasta` (default ~512 MB; scale with `--size-mb`).
- Target pattern: `b"AGTCCGTA"` (recorded in `data/truth.json`).
- Output: `list[tuple[record_id, list[int positions]]]` in file order.

You are encouraged to combine techniques from rounds 1 and 2.

## Files

| File          | Purpose                                                                                                                   |
| ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `baseline.py` | Intentionally slow starting point. **Don't edit:** it is the reference for the comparison.                                |
| `solution.py` | **Edit this.** Starts out delegating to `baseline.py`; replace with your faster implementation.                           |
| `gen_data.py` | Generates the FASTA file and a `truth.json` with expected matches.                                                        |
| `test_dna.py` | Correctness tests and the pytest-codspeed benchmark. Every test is parametrized over both the baseline and your solution. |

## Generate the data

```bash
uv run rounds/3_dna/gen_data.py             # default ~512 MB.
uv run rounds/3_dna/gen_data.py --size-mb 100
```

Or run `uv run scripts/setup.py` to generate every round's data in one go.

## Verify correctness

```bash
uv run pytest rounds/3_dna/
```

## Benchmark

Walltime, locally:

```bash
uv run pytest --codspeed rounds/3_dna/
```

Same benchmarks, run through the CodSpeed CLI for low-noise instrumented
measurements:

```bash
codspeed run uv run pytest --codspeed rounds/3_dna/
```

## Toolbox for this round

You do not need all of these. Pick a few and measure.

- Stay in `bytes` end-to-end and let `bytes.find()` do the search in C.
- Stream the file with `readinto()` into a reusable `bytearray` instead of
  slurping; parse records on the fly.
- Use a `memoryview` over the buffer so record slicing does not copy.
- Vectorize with NumPy: view a chunk as `np.uint8`, build a boolean mask of
  candidate match positions, then resolve full matches.
- On free-threaded CPython, split the file into byte ranges and search them
  in parallel; reconcile records that cross chunk boundaries in a final pass.
- Keep only a small top-K heap if the leaderboard scores on the hottest
  records, so memory stays bounded as the dataset grows.
