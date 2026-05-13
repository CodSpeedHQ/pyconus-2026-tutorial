# Round 3 (Final Challenge) — DNA sequence matcher

## Problem

Given a FASTA-like file (`genome.fasta`) containing DNA sequences using only
`A`, `C`, `G`, `T`, find **every record whose sequence contains a target
pattern**, along with the positions of each occurrence inside that record.

- Input: `data/genome.fasta` (default ~512 MB; scale with `--size-mb`)
- Target pattern: `b"AGTCCGTA"` (recorded in `data/truth.json`)
- Output: `list[tuple[record_id, list[int positions]]]` in file order

This is the **team challenge** at the end of the tutorial. Encouraged to
combine techniques from Rounds 1 and 2 — there's a live leaderboard.

## What "fast" means here

End-to-end wall time. Memory matters too — the file can be larger than RAM if
you push `--size-mb` up. The best solutions stream the file and search inside
C-level routines.

## Files

| File | Purpose |
|---|---|
| `baseline.py` | The intentionally slow starting point. **Don't edit** — it's the reference for the comparison. |
| `solution.py` | **Edit this.** Starts out delegating to `baseline.py`; replace with your faster implementation. |
| `gen_data.py` | Generates the FASTA file and a `truth.json` with expected matches. |
| `test_dna.py` | Correctness tests + pytest-codspeed benchmark. Every test is parametrized to run against both the baseline and your solution. |

## Generate the data

```bash
python rounds/3_dna/gen_data.py             # default ~512 MB
python rounds/3_dna/gen_data.py --size-mb 100
```

## Verify correctness

```bash
uv run pytest rounds/3_dna/
```

## Benchmark

```bash
uv run pytest --codspeed rounds/3_dna/
```

## Toolbox for this round

This round rewards combining techniques from earlier rounds:

- **Bytes end-to-end** (Round 1): never `.decode()` the file.
- **Streaming + buffer reuse** (Round 2): parse records as they're read; don't
  slurp the file.
- **C-level search** : `bytes.find()` over chunks beats anything you'll
  write in Python.
- **Parallelism**: split the file into byte ranges, scan in parallel, then
  reconcile records that cross chunk boundaries.
- **Top-K without sorting** (introduced if needed): if the leaderboard scores
  on "top K hottest records," keep a small heap as you stream results.
