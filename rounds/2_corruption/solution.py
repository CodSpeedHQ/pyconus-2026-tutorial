from __future__ import annotations

import numpy as np


def find_corruptions(ref_path: str, cor_path: str) -> list[tuple[int, int]]:
    """Return ``[(offset, length), ...]`` for every differing byte range."""
    with open(ref_path, "rb") as f:
        ref = np.frombuffer(f.read(), dtype=np.uint8)
    with open(cor_path, "rb") as f:
        cor = np.frombuffer(f.read(), dtype=np.uint8)

    if len(ref) != len(cor):
        raise ValueError("reference and corrupted files differ in length")

    # Boolean mask of differing positions
    mask = ref != cor
    if not mask.any():
        return []

    # Find run boundaries using diff on the mask
    padded = np.empty(len(mask) + 2, dtype=np.int8)
    padded[0] = 0
    padded[1:-1] = mask.view(np.int8)
    padded[-1] = 0
    d = np.diff(padded.astype(np.int8))
    starts = np.where(d == 1)[0]
    ends = np.where(d == -1)[0]

    return [(int(s), int(e - s)) for s, e in zip(starts, ends)]
