"""Your Round 1 solution — byte-pair histogram."""

import numpy as np
import mmap


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    with open(path, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # Copy while mmap is still open — no exported pointer issue
            data = np.frombuffer(mm, dtype=np.uint8).copy()
        keys = data[:-1].astype(np.uint16) << 8 | data[1:].astype(np.uint16)
        counts = np.bincount(keys, minlength=65536)
    return {bytes([k >> 8, k & 0xFF]): int(counts[k]) for k in np.nonzero(counts)[0]}
