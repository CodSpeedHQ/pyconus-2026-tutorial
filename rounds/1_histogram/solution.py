"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""
from collections import defaultdict


def compute_histogram(path: str) -> dict[bytes, int]:

    """Frequency of every 2-byte bigram in the file at ``path``."""
    counts: dict[bytes, int] = defaultdict(int)

    with open(path, "rb") as f:
        data = f.read()

    for i in range(len(data) - 1):
        counts[data[i:i + 2]] += 1

    return dict(counts)
