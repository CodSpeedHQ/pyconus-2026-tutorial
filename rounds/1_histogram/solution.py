"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    with open(path, "rb") as f:
        data = f.read()
    counts: dict[bytes, int] = {}
    bigrams_seen = set()
    for i in range(len(data) - 1):
        bigram = data[i : i + 2]
        if bigram in bigrams_seen:
            counts[bigram] += 1
        else:
            bigrams_seen.add(bigram)
            counts[bigram] = 1
    return counts
