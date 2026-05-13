"""Round 1 solution — byte-pair histogram."""

import numpy as np


def compute_histogram(path: str) -> dict[bytes, int]:
    data = np.fromfile(path, dtype=np.uint8)
    if len(data) < 2:
        return {}

    bigrams = (data[:-1].astype(np.uint16) << 8) | data[1:]

    counts = np.bincount(bigrams, minlength=65536)

    valid_indices = np.nonzero(counts)[0]
    valid_counts = counts[valid_indices]

    return {
        int(idx).to_bytes(2, 'big'): int(count) 
        for idx, count in zip(valid_indices, valid_counts)
    }
