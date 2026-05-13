"""Your Round 1 solution — byte-pair histogram.

This version keeps the same contract as ``baseline.py`` but replaces the
per-bigram Python loop with NumPy operations over the whole byte buffer.
"""

from __future__ import annotations
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent / "data"
FIXTURE_PATH = DATA_DIR / "fixture_payload.bin"


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""

    # Read the whole file into memory as a single bytes object
    with open(path, 'rb') as f:
        data = f.read()

    # Expose the bytes object as a uint8 NumPy array without copying
    byte_values = np.frombuffer(data, dtype=np.uint8)

    # Encode each overlapping 2-byte window as a uint16 token
    bigrams = byte_values[:-1].astype(np.uint16)
    bigrams <<= 8
    bigrams |= byte_values[1:]

    # Count the uint16 tokens directly
    counts = np.bincount(bigrams, minlength=1 << 16)

    # Convert back into the return format
    return {
        int(token).to_bytes(2, "big"): int(count)
        for token, count in enumerate(counts)
        if count
    }


if __name__ == '__main__':
    compute_histogram(str(FIXTURE_PATH))
