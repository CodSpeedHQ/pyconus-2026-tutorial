"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    with open(path, "rb") as f:
        data = f.read()

    counts = [[0] * 256 for _ in range(256)]
    for i in range(len(data) - 1):
        counts[data[i]][data[i + 1]] += 1
    return {bytes((i, j)): counts[i][j] for i in range(256) for j in range(256)}
