"""Generate the Round 1 dataset: a binary payload with biased byte frequencies.

Run from anywhere:

    uv run rounds/1_histogram/gen_data.py            # default 10 MB
    uv run rounds/1_histogram/gen_data.py --size-mb 50

Output:
    rounds/1_histogram/data/payload.bin           — full benchmark dataset
    rounds/1_histogram/data/fixture_payload.bin   — tiny fixture for tests
"""

from __future__ import annotations

import argparse
import os
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

FIXTURE_SIZE_BYTES = 64 * 1024  # 64 KB fixture — fast, deterministic


def _biased_alphabet() -> bytes:
    """Skew byte frequencies so the histogram is non-trivial.

    A flat-random payload makes every bucket land near the mean, which hides
    bugs in attendee implementations. We instead bias toward a smaller alphabet
    with realistic-looking long tails.
    """
    common = b"ETAOINSHRDLU "  # frequent ASCII letters + space
    medium = b"abcdefghijklmnopqrstuvwxyz0123456789\n"
    rare = bytes(range(256))
    return common * 40 + medium * 8 + rare


def _write_payload(path: Path, size_bytes: int, seed: int) -> None:
    rng = random.Random(seed)
    alphabet = _biased_alphabet()
    chunk_size = 1 << 20  # 1 MB at a time keeps peak memory low
    remaining = size_bytes
    with path.open("wb") as f:
        while remaining > 0:
            n = min(chunk_size, remaining)
            f.write(bytes(rng.choices(alphabet, k=n)))
            remaining -= n


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--size-mb",
        type=int,
        default=10,
        help="Size of the full benchmark payload in MB (default: 10).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic output (default: 42).",
    )
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    full_path = DATA_DIR / "payload.bin"
    fixture_path = DATA_DIR / "fixture_payload.bin"

    print(f"writing fixture: {fixture_path} ({FIXTURE_SIZE_BYTES} bytes)")
    _write_payload(fixture_path, FIXTURE_SIZE_BYTES, seed=args.seed + 1)

    full_size = args.size_mb * 1024 * 1024
    print(f"writing payload: {full_path} ({args.size_mb} MB)")
    _write_payload(full_path, full_size, seed=args.seed)

    print(f"done. total on disk: {os.path.getsize(full_path) + os.path.getsize(fixture_path):,} bytes")


if __name__ == "__main__":
    main()
