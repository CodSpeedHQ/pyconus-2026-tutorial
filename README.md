# Python Performance Lab: Sharpening Your Instincts

A PyCon US 2026 hands-on tutorial. You optimize intentionally slow Python code
across three rounds plus a team challenge, measuring every change with
[CodSpeed](https://codspeed.io)...

## Rounds

| Round                      | Topic                | Skills                                |
| -------------------------- | -------------------- | ------------------------------------- |
| [1](rounds/1_histogram/)   | Byte-pair histogram  | Data representation, vectorization    |
| [2](rounds/2_corruption/)  | Corruption scanner   | Vectorization, parallelism            |
| [3](rounds/3_dna/) (final) | DNA sequence matcher | Everything above, as a team challenge |

Each round ships an intentionally slow `baseline.py` (a read-only reference),
a `solution.py` you edit, deterministic data generators, parametrized
correctness tests, and benchmarks that run baseline and solution
side-by-side.

## Setup

You need [`uv`](https://docs.astral.sh/uv/). Python 3.15t will be downloaded directly.

The order below matters: forking, logging in, and doing the first run on `main`
register you on the live leaderboard, so every later push to your branch shows
up as a side-by-side comparison against your own baseline.

```bash
# 1. Fork github.com/CodSpeedHQ/pyconus-2026-tutorial, then clone your fork.
git clone https://github.com/<you>/pyconus-2026-tutorial && cd pyconus-2026-tutorial
# or better, use the GitHub CLI:
gh repo fork CodSpeedHQ/pyconus-2026-tutorial --clone=true && cd pyconus-2026-tutorial

# 2. Install deps + generate the datasets (~650 MB total).
uv sync
uv run scripts/setup.py

# 3. Install the CodSpeed CLI and log in.
curl -L https://codspeed.io/install.sh | sh
codspeed auth login

# 4. Make a first CodSpeed local run and access the performance report
codspeed run --mode walltime -- uv run pytest --codspeed

# 5. Branch off and create a pr on the main repo. Every push to this branch re-runs and re-ranks you.
git checkout -b <your-name>
# Make a small change like adding your name in the README.md for example, and commit:
echo "This is <your-name>'s PR" >> README.md
git add README.md
git commit -m "Add <your-name> to the README"
# Push and open a PR against the main repo:
gh pr create --title "[username] performance improvements" --base main --repo CodSpeedHQ/pyconus-2026-tutorial
```

Generate smaller datasets on lower-spec machines:

```bash
uv run scripts/setup.py --round1-mb 10 --round2-mb 32 --round3-mb 100
```

## Working on a round

Every round directory ships its own `README.md`. The commands are the same
shape every time, illustrated here for Round 1:

```bash
# Correctness tests against the small fixture.
uv run pytest rounds/1_histogram/

# Walltime benchmark against the full dataset.
uv run pytest --codspeed rounds/1_histogram/

# Same, run through the CodSpeed CLI with the walltime mode
codspeed run --mode walltime -- uv run pytest --codspeed rounds/1_histogram/
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
