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

    # Step 2: slide a 2-byte window across the buffer. For ``b"ABCD"`` the
    # iterations produce ``b"AB"``, ``b"BC"``, then ``b"CD"``. For each window,
    # bump the matching bucket in a ``dict`` keyed by the bigram itself.
    counts= [[0] * 256 for _ in range(256)]
    
    for i in range(len(data) - 1):
        a, b = data[i], data[i + 1]
        counts[a][b] += 1

    result = {}
    for i, row in enumerate(counts):
        for j, count in enumerate(row):
            if count > 0:
                bigram = bytes([i, j])
                result[bigram] = count
    return result