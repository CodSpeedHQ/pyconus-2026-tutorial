"""Round 1 baseline — byte-pair histogram.

Counts the frequency of every 2-byte bigram (256 * 256 = 65,536 possible tokens)
in a binary payload.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    with open(path, "rb") as f:
        data = f.read()

    counts: dict[bytes, int] = {}
    for i in range(len(data) - 1):
        bigram = data[i : i + 2]
        if bigram in counts:
            counts[bigram] += 1
        else:
            counts[bigram] = 1
    return counts
