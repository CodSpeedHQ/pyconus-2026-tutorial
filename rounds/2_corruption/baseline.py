"""Round 2 baseline — corruption scanner.

Compares two equally-sized binary files and reports every contiguous run of
differing bytes as ``(offset, length)``.
"""

from __future__ import annotations


def find_corruptions(ref_path: str, cor_path: str) -> list[tuple[int, int]]:
    """Return ``[(offset, length), ...]`` for every differing byte range."""
    with open(ref_path, "rb") as f:
        ref = f.read()
    with open(cor_path, "rb") as f:
        cor = f.read()
    if len(ref) != len(cor):
        raise ValueError("reference and corrupted files differ in length")

    diffs: list[int] = []
    for i in range(len(ref)):
        if ref[i] != cor[i]:
            diffs.append(i)

    ranges: list[tuple[int, int]] = []
    if not diffs:
        return ranges
    start = diffs[0]
    prev = diffs[0]
    for pos in diffs[1:]:
        if pos == prev + 1:
            prev = pos
        else:
            ranges.append((start, prev - start + 1))
            start = pos
            prev = pos
    ranges.append((start, prev - start + 1))
    return ranges
