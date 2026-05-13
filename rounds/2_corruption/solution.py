"""Your Round 2 solution — corruption scanner.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_corruptions`` with your
own faster implementation.
"""

import numpy as np


def find_corruptions(ref_path: str, cor_path: str) -> list[tuple[int, int]]:
    """Return ``[(offset, length), ...]`` for every differing byte range."""
    ref = np.fromfile(ref_path, dtype=np.uint8)
    cor = np.fromfile(cor_path, dtype=np.uint8)

    if len(ref) != len(cor):
        raise ValueError("reference and corrupted files differ in length")

    # Single vectorised comparison — runs entirely in C.
    diff_indices = np.where(ref != cor)[0]

    if len(diff_indices) == 0:
        return []

    # Find the boundaries between consecutive runs.
    # A new run starts wherever the gap between adjacent indices exceeds 1.
    gaps = np.where(np.diff(diff_indices) > 1)[0]
    starts = diff_indices[np.concatenate(([0], gaps + 1))]
    ends = diff_indices[np.concatenate((gaps, [len(diff_indices) - 1]))]

    return [(int(s), int(e - s + 1)) for s, e in zip(starts, ends)]
