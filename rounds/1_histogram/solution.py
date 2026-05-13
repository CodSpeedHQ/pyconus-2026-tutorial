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

    # Vectorised bigram index: first_byte * 256 + second_byte
    bigram_indices = arr[:-1].astype(np.uint16) * 256 + arr[1:]

    # Count every bigram in a single pass (C-level loop inside numpy)
    counts = np.bincount(bigram_indices, minlength=65536)

    # Build the result dict from non-zero entries only
    nonzero = np.flatnonzero(counts)
    return {int(idx).to_bytes(2, "big"): int(counts[idx]) for idx in nonzero}
