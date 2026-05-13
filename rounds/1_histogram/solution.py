"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""
import numpy as np
 
def compute_histogram(path: str) -> dict[bytes, int]:

    """Frequency of every 2-byte bigram in the file at ``path``."""

    data = np.fromfile(path, dtype=np.uint8)

    if len(data) < 2:

        return {}

    bigrams = (data[:-1].astype(np.uint16) << 8) | data[1:]

    counts = np.bincount(bigrams, minlength=65536)

    return {bytes([idx >> 8, idx & 0xFF]): int(count) for idx, count in enumerate(counts) if count > 0}

 