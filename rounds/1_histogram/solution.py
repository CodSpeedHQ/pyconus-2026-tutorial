"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""
from collections import Counter


def get_biagrams(data):
    i = 0
    max_len = len(data) -1
    while i < max_len:
        biagram = data[i: i + 2]
        yield biagram
        i += 1


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # Step 1: read the whole file into memory as a single bytes object.
    with open(path, "rb") as f:
        data = f.read()

    # Step 2: slide a 2-byte window across the buffer. For ``b"ABCD"`` the
    # iterations produce ``b"AB"``, ``b"BC"``, then ``b"CD"``. For each window,
    # bump the matching bucket in a ``dict`` keyed by the bigram itself.
    counts = Counter(get_biagrams(data))
    return counts
