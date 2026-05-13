"""Generate the Round 3 dataset: a FASTA-like file with known pattern hits.

Run from anywhere:

    python rounds/3_dna/gen_data.py            # default ~1 GB
    python rounds/3_dna/gen_data.py --size-mb 100

Output:
    rounds/3_dna/data/genome.fasta
    rounds/3_dna/data/truth.json
    rounds/3_dna/data/fixture_genome.fasta
    rounds/3_dna/data/fixture_truth.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

ALPHABET = b"ACGT"
PATTERN = b"AGTCCGTA"  # the pattern attendees will search for
LINE_WIDTH = 80


def _random_seq(rng: random.Random, length: int) -> bytearray:
    return bytearray(rng.choices(ALPHABET, k=length))


def _inject_pattern(seq: bytearray, rng: random.Random, pattern: bytes, count: int) -> list[int]:
    """Overwrite ``count`` slots in ``seq`` with ``pattern`` at random offsets."""
    placed: list[int] = []
    attempts = 0
    while len(placed) < count and attempts < count * 10:
        attempts += 1
        offset = rng.randrange(0, len(seq) - len(pattern))
        # avoid stacking patterns on top of each other for stable ground truth
        if any(abs(offset - p) < len(pattern) for p in placed):
            continue
        seq[offset : offset + len(pattern)] = pattern
        placed.append(offset)
    placed.sort()
    return placed


def _write_fasta(
    out_path: Path,
    truth_path: Path,
    target_size: int,
    seed: int,
    pattern: bytes,
    inject_every_n: int,
) -> None:
    rng = random.Random(seed)
    truth: list[tuple[str, list[int]]] = []

    written = 0
    record_idx = 0
    with out_path.open("wb") as f:
        while written < target_size:
            record_idx += 1
            record_id = f"seq_{record_idx:06d}"
            seq_len = rng.randint(5_000, 100_000)

            seq = _random_seq(rng, seq_len)
            positions: list[int] = []
            if record_idx % inject_every_n == 0:
                positions = _inject_pattern(
                    seq, rng, pattern, count=rng.randint(1, 4)
                )

            # Also scan for accidental occurrences of the pattern.
            seq_bytes = bytes(seq)
            scan = 0
            while True:
                idx = seq_bytes.find(pattern, scan)
                if idx == -1:
                    break
                if idx not in positions:
                    positions.append(idx)
                scan = idx + 1
            positions.sort()
            if positions:
                truth.append((record_id, positions))

            header = f">{record_id}\n".encode("ascii")
            f.write(header)
            written += len(header)
            for offset in range(0, len(seq), LINE_WIDTH):
                f.write(seq_bytes[offset : offset + LINE_WIDTH])
                f.write(b"\n")
                written += min(LINE_WIDTH, len(seq) - offset) + 1

    truth_path.write_text(
        json.dumps(
            {
                "pattern": pattern.decode("ascii"),
                "matches": [[rid, list(p)] for rid, p in truth],
            },
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size-mb", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    fixture_fasta = DATA_DIR / "fixture_genome.fasta"
    fixture_truth = DATA_DIR / "fixture_truth.json"
    print(f"writing fixture: {fixture_fasta} (~512 KB)")
    _write_fasta(
        fixture_fasta,
        fixture_truth,
        target_size=512 * 1024,
        seed=args.seed + 100,
        pattern=PATTERN,
        inject_every_n=3,
    )

    full_fasta = DATA_DIR / "genome.fasta"
    full_truth = DATA_DIR / "truth.json"
    full_size = args.size_mb * 1024 * 1024
    print(f"writing genome: {full_fasta} (~{args.size_mb} MB)")
    _write_fasta(
        full_fasta,
        full_truth,
        target_size=full_size,
        seed=args.seed,
        pattern=PATTERN,
        inject_every_n=5,
    )

    total = os.path.getsize(full_fasta) + os.path.getsize(fixture_fasta)
    print(f"done. total on disk: {total:,} bytes")


if __name__ == "__main__":
    main()
