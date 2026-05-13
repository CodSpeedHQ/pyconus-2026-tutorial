"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""


# def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # TODO: Used chatgpt for optimization of byte-pair histogram 
   # from .baseline import compute_histogram as _baseline

    #return _baseline(path)

from array import array


def compute_histogram(path: str) -> list[int]:
    """
    Frequency table for every 2-byte bigram.

    Result index:
        index = (byte1 << 8) | byte2

    Example:
        b"AB" -> (65 << 8) | 66
    """
    with open(path, "rb") as f:
        data = f.read()

    n = len(data)
    if n < 2:
        return [0] * 65536

    # Fixed-size contiguous integer array
    counts = array('I', [0]) * 65536

    prev = data[0]

    for i in range(1, n):
        curr = data[i]
        counts[(prev << 8) | curr] += 1
        prev = curr

    return counts
