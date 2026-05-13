"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""

from array import array


def compute_histogram(path: str) -> dict[bytes, int]:
    with open(path, "rb") as f:
        data = f.read()

    n = len(data)
    if n < 2:
        return {}

    # 65,536 possible 2-byte combinations
    counts = array("I", [0]) * 65536

    prev = data[0]

    for i in range(1, n):
        curr = data[i]
        counts[(prev << 8) | curr] += 1
        prev = curr

    return {
        i.to_bytes(2, "big"): count
        for i, count in enumerate(counts)
        if count
    }