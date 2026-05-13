"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""

import numpy as np


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # Step 1: read the whole file into memory as a single bytes object.
    with open(path, "rb") as f:
        data = f.read()

    raw = np.frombuffer(data, dtype=np.uint8)
    bigrams = raw[:-1].astype(np.uint16) * 256 + raw[1:]
    unique, freq = np.unique(bigrams, return_counts=True)
    return {int(u).to_bytes(2, "big"): int(c) for u, c in zip(unique, freq)}
