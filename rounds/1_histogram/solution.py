"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""
from collections import defaultdict
from mmap import mmap, ACCESS_READ

def b2i(low: int, high: int) -> int:
    return high + (low << 8)

def i2b(x: int) -> bytes:
    return bytes([(x & 0xFF00) >> 8, x & 0xFF])

def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # Step 1: read the whole file into memory as a single bytes object.
    counts = [0 for _ in range(2**16)]

    source = open(path, "rb", buffering=0)
    data = mmap(source.fileno(), 0, access=ACCESS_READ)

    # Step 2: slide a 2-byte window across the buffer. For ``b"ABCD"`` the
    # iterations produce ``b"AB"``, ``b"BC"``, then ``b"CD"``. For each window,
    # bump the matching bucket in a ``dict`` keyed by the bigram itself.
    previous = data[0]
    for i in range(len(data) - 1):
        current = data[i + 1]
        counts[current + (previous << 8)] += 1
        previous = current

    return {
        i2b(idx): value for idx, value in enumerate(counts) if value != 0
    }
