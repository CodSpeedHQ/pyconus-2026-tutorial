"""Round 1 baseline: byte-pair histogram.

Counts the frequency of every 2-byte bigram (256 * 256 = 65,536 possible
tokens) in a binary payload.
"""

from collections import Counter
from itertools import pairwise


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    with open(path, "rb") as f:
        data = f.read()

    return Counter(bytes(bigram) for bigram in pairwise(data))
