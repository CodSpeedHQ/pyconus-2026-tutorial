"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""

from collections import Counter
from itertools import pairwise
from pathlib import Path


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    return Counter(bytes(bigram) for bigram in pairwise(Path(path).read_bytes()))
