"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""

from concurrent.futures import ProcessPoolExecutor
import os

CHUNK_SIZE = 8 * 1024 * 1024

def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # TODO: remove this delegation and write your own implementation here.
    with open(path, "rb") as f:
        data = f.read()

    counts: list[int] = [0] * 65536
    if len(data) == 0:
        return {}
    data_iter = iter(data)
    window_idx = next(data_iter)
    for b in data_iter:
        window_idx <<= 8
        window_idx &= 0xff00
        window_idx |= b
        counts[window_idx] += 1
    d = {}
    for i,cnt in enumerate(counts):
        if counts[i] != 0:
            b = i.to_bytes(2, byteorder="big")
            d[b] = cnt
    return d
