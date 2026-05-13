"""Round 1 solution — byte-pair histogram."""


import numpy as np


def compute_histogram(path: str) -> dict[bytes, int]:
    data = np.fromfile(path, dtype=np.uint8)
    if len(data) < 2:
        return {}

    bigrams_16 = (data[:-1].astype(np.uint16) << 8) | data[1:]
    
    values, counts = np.unique(bigrams_16, return_counts=True)
    
    return {int(v).to_bytes(2, 'big'): int(c) for v, c in zip(values, counts)}
