# Python Performance Lab: Sharpening Your Instincts

PyCon US 2026 tutorial — hands-on Python performance work.

You'll work in **optimization rounds**: each starts from a purposely slow
baseline and ends with a faster, leaner solution. Three rounds plus a final
team challenge.

| Round | Topic | Theme |
|---|---|---|
| [1](rounds/1_histogram/) | Byte-pair histogram | Data representation + memory |
| [2](rounds/2_corruption/) | Corruption scanner | Streaming + parallelism + vectorization |
| [3](rounds/3_dna/) (final) | DNA sequence matcher | Everything together, team challenge |

## Setup

You'll need Python 3.13 or newer and [`uv`](https://docs.astral.sh/uv/).

```bash
uv sync                              # install pytest, pytest-codspeed, numpy
python scripts/setup.py              # generate all datasets (~1.3 GB total)
```

Smaller machines:

```bash
python scripts/setup.py --round1-mb 20 --round2-mb 64 --round3-mb 100
```

## Run a round

Each round directory has its own `README.md`. The shape is always the same:

```bash
# correctness (fast — runs against a small fixture)
uv run pytest rounds/1_histogram/

# benchmark (local timing; runs against the full dataset)
uv run pytest --codspeed rounds/1_histogram/

# benchmark via CodSpeed CLI (instrumented)
codspeed run uv run pytest --codspeed rounds/1_histogram/
```

Optimize by editing the **`solution.py`** in that round (not `baseline.py` —
the baseline stays put as the reference for comparison). Every test and
benchmark runs against both implementations, so the output always shows
`[baseline]` vs `[solution]` side-by-side.

## Repository layout

```
rounds/
  1_histogram/        # baseline.py + gen_data.py + tests + benches
  2_corruption/
  3_dna/
scripts/
  setup.py                 # one-shot data generation
```

The `data/` directory inside each round is **generated locally** (gitignored).
