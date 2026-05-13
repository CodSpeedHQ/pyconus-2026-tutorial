"""Generate the Round 2 dataset: a reference blob and a corrupted twin.

Run from anywhere:

    python rounds/2_corruption/gen_data.py             # default 64 MB
    python rounds/2_corruption/gen_data.py --size-mb 1024

Output:
    rounds/2_corruption/data/reference.bin
    rounds/2_corruption/data/corrupted.bin
    rounds/2_corruption/data/truth.json
    rounds/2_corruption/data/fixture_reference.bin
    rounds/2_corruption/data/fixture_corrupted.bin
    rounds/2_corruption/data/fixture_truth.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

FIXTURE_SIZE_BYTES = 256 * 1024  # 256 KB fixture


def _write_random_blob(path: Path, size_bytes: int, seed: int) -> None:
    rng = random.Random(seed)
    chunk_size = 1 << 20
    remaining = size_bytes
    with path.open("wb") as f:
        while remaining > 0:
            n = min(chunk_size, remaining)
            f.write(rng.randbytes(n))
            remaining -= n


def _inject_corruptions(
    ref_path: Path, cor_path: Path, seed: int, count: int
) -> list[tuple[int, int]]:
    """Copy ``ref_path`` into ``cor_path``, flipping bytes at random ranges.

    Returns the list of injected ``(offset, length)`` corruption ranges,
    sorted by offset and guaranteed non-overlapping.
    """
    size = ref_path.stat().st_size
    rng = random.Random(seed)

    # Pick non-overlapping ranges of length 1–64 bytes.
    chosen: list[tuple[int, int]] = []
    attempts = 0
    while len(chosen) < count and attempts < count * 10:
        attempts += 1
        length = rng.randint(1, 64)
        offset = rng.randrange(0, size - length)
        if any(
            offset < o + l and o < offset + length for o, l in chosen
        ):
            continue
        chosen.append((offset, length))
    chosen.sort()

    # Stream-copy reference → corrupted, flipping bytes inside chosen ranges.
    # We keep an index into the sorted-range list and advance it per chunk.
    chunk_size = 1 << 20
    range_iter = iter(chosen)
    next_range = next(range_iter, None)
    with ref_path.open("rb") as src, cor_path.open("wb") as dst:
        pos = 0
        while True:
            buf = bytearray(src.read(chunk_size))
            if not buf:
                break
            end = pos + len(buf)
            while next_range is not None and next_range[0] < end:
                r_off, r_len = next_range
                lo = max(r_off, pos) - pos
                hi = min(r_off + r_len, end) - pos
                for i in range(lo, hi):
                    # XOR with a non-zero mask so the flipped byte differs.
                    buf[i] ^= 0xA5 if buf[i] != 0xA5 else 0x5A
                if r_off + r_len <= end:
                    next_range = next(range_iter, None)
                else:
                    break
            dst.write(buf)
            pos = end

    return chosen


def _generate(
    target_size: int,
    seed: int,
    corruption_count: int,
    name_prefix: str,
) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ref = DATA_DIR / f"{name_prefix}reference.bin"
    cor = DATA_DIR / f"{name_prefix}corrupted.bin"
    truth = DATA_DIR / f"{name_prefix}truth.json"

    print(f"writing reference: {ref} ({target_size:,} bytes)")
    _write_random_blob(ref, target_size, seed=seed)

    print(f"writing corrupted: {cor} (with {corruption_count} injected ranges)")
    ranges = _inject_corruptions(ref, cor, seed=seed + 1, count=corruption_count)

    truth.write_text(json.dumps({"size": target_size, "ranges": ranges}, indent=2))
    print(f"wrote truth: {truth} ({len(ranges)} ranges)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size-mb", type=int, default=64)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--corruptions",
        type=int,
        default=200,
        help="Number of corruption ranges to inject into the full payload.",
    )
    args = parser.parse_args()

    print("--- fixture ---")
    _generate(
        target_size=FIXTURE_SIZE_BYTES,
        seed=args.seed + 100,
        corruption_count=20,
        name_prefix="fixture_",
    )

    print("--- full dataset ---")
    _generate(
        target_size=args.size_mb * 1024 * 1024,
        seed=args.seed,
        corruption_count=args.corruptions,
        name_prefix="",
    )

    total = sum(
        os.path.getsize(p)
        for p in (
            DATA_DIR / "reference.bin",
            DATA_DIR / "corrupted.bin",
            DATA_DIR / "fixture_reference.bin",
            DATA_DIR / "fixture_corrupted.bin",
        )
    )
    print(f"done. total on disk: {total:,} bytes")


if __name__ == "__main__":
    main()
