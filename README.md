# Python Performance Lab: Sharpening Your Instincts

A PyCon US 2026 hands-on tutorial. You optimize intentionally slow Python code
across three rounds plus a team challenge, measuring every change with
[CodSpeed](https://codspeed.io).

## Rounds

| Round                      | Topic                | Skills                                |
| -------------------------- | -------------------- | ------------------------------------- |
| [1](rounds/1_histogram/)   | Byte-pair histogram  | Data representation, memory           |
| [2](rounds/2_corruption/)  | Corruption scanner   | Streaming, parallelism, vectorization |
| [3](rounds/3_dna/) (final) | DNA sequence matcher | Everything above, as a team challenge |

Each round ships an intentionally slow `baseline.py` (a read-only reference),
a `solution.py` you edit, deterministic data generators, parametrized
correctness tests, and benchmarks that run baseline and solution
side-by-side.

## Setup

You need [`uv`](https://docs.astral.sh/uv/) and Python 3.15t.

```bash
uv sync                   # install pytest, pytest-codspeed, numpy.
python scripts/setup.py   # generate all datasets (~650 MB total).
```

Generate smaller datasets on lower-spec machines:

```bash
python scripts/setup.py --round1-mb 10 --round2-mb 32 --round3-mb 100
```

## Working on a round

Every round directory ships its own `README.md`. The commands are the same
shape every time, illustrated here for Round 1:

```bash
# Correctness tests against the small fixture.
uv run pytest rounds/1_histogram/

# Walltime benchmark against the full dataset.
uv run pytest --codspeed rounds/1_histogram/

# Same, run through the CodSpeed CLI for low-noise instrumented measurements.
codspeed run uv run pytest --codspeed rounds/1_histogram/
```

Edit `solution.py` to optimize. Leave `baseline.py` alone so the side-by-side
comparison stays meaningful. Every test and benchmark is parametrized over
both implementations, so the output always shows `[baseline]` versus
`[solution]`.

## Layout

```
rounds/
  1_histogram/             # baseline.py, solution.py, gen_data.py, tests.
  2_corruption/
  3_dna/
scripts/
  setup.py                 # one-shot data generation across every round.
```

Each round's `data/` directory is generated locally and gitignored.
