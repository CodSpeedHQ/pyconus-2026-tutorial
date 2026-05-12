"""One-shot dataset generation for every round.

Run from the repo root:

    uv run scripts/setup.py                       # default sizes
    uv run scripts/setup.py --round1-mb 50        # smaller payloads on slow disks
    uv run scripts/setup.py --skip round2 round3  # just round 1
    uv run scripts/setup.py --seed 1337           # different deterministic data
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

ROUNDS = {
    "round1": REPO_ROOT / "rounds" / "1_histogram" / "gen_data.py",
    "round2": REPO_ROOT / "rounds" / "2_corruption" / "gen_data.py",
    "round3": REPO_ROOT / "rounds" / "3_dna" / "gen_data.py",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--round1-mb", type=int, default=10)
    parser.add_argument("--round2-mb", type=int, default=64)
    parser.add_argument("--round3-mb", type=int, default=512)
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help=(
            "Override the deterministic seed used by every round's generator. "
            "When omitted, each round uses its own built-in default."
        ),
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        default=[],
        choices=list(ROUNDS),
        help="Round names to skip.",
    )
    args = parser.parse_args()

    shared = []
    if args.seed is not None:
        shared = ["--seed", str(args.seed)]

    extra_args = {
        "round1": ["--size-mb", str(args.round1_mb), *shared],
        "round2": ["--size-mb", str(args.round2_mb), *shared],
        "round3": ["--size-mb", str(args.round3_mb), *shared],
    }

    for name, script in ROUNDS.items():
        if name in args.skip:
            print(f"== {name}: skipped")
            continue
        print(f"== {name}: {script}")
        result = subprocess.run(
            [sys.executable, str(script), *extra_args[name]],
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(f"!! {name} failed (exit {result.returncode})")
            return result.returncode

    print("\nAll datasets generated. You can now run:")
    print("    uv run pytest rounds/                  # correctness")
    print("    uv run pytest --codspeed rounds/       # benchmarks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
