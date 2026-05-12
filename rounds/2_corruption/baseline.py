"""Round 2 baseline: corruption scanner.

Compares two equally-sized binary files and reports every contiguous run of
differing bytes as ``(offset, length)``.
"""

from __future__ import annotations


def find_corruptions(ref_path: str, cor_path: str) -> list[tuple[int, int]]:
    """Return ``[(offset, length), ...]`` for every differing byte range."""
    # Step 1: read both files fully into memory as bytes objects.
    with open(ref_path, "rb") as f:
        ref = f.read()
    with open(cor_path, "rb") as f:
        cor = f.read()
    if len(ref) != len(cor):
        raise ValueError("reference and corrupted files differ in length")

    # Step 2: walk both buffers in lockstep and record every position where
    # the two files disagree. The result is a sorted list of standalone byte
    # offsets, e.g. [3, 4, 5, 17, 18].
    diffs: list[int] = []
    for i in range(len(ref)):
        if ref[i] != cor[i]:
            diffs.append(i)

    # Step 3: collapse runs of consecutive offsets into (start, length) ranges.
    # The list from step 2 becomes [(3, 3), (17, 2)]: starting at 3 there are
    # three differing bytes, then starting at 17 there are two more.
    if not diffs:
        return []
    ranges: list[tuple[int, int]] = []
    start = diffs[0]
    prev = diffs[0]
    for pos in diffs[1:]:
        if pos == prev + 1:
            # Still inside the current run; extend it.
            prev = pos
        else:
            # Gap. Close the current run and start a new one.
            ranges.append((start, prev - start + 1))
            start = pos
            prev = pos
    ranges.append((start, prev - start + 1))  # Close the final run.
    return ranges
