"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""

import numpy as np


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    with open(path, "rb") as f:
        data = f.read()

    arr = np.frombuffer(data, dtype=np.uint8)
    # Encode each bigram as a uint16 index: high_byte * 256 + low_byte
    indices = arr[:-1].astype(np.uint16) * 256 + arr[1:]
    counts = np.bincount(indices, minlength=65536)

    result: dict[bytes, int] = {}
    for idx in np.nonzero(counts)[0]:
        result[bytes([idx >> 8, idx & 0xFF])] = int(counts[idx])
    return result
