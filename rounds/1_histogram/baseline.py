"""Round 1 baseline — byte-pair histogram.

Counts the frequency of every 2-byte bigram (256 * 256 = 65,536 possible tokens)
in a binary payload. This baseline is *intentionally* slow: every choice below is
something attendees should be able to spot and improve.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # Anti-pattern: text-mode read forces a latin-1 round-trip and allocates
    # both a giant `str` and (below) a giant `bytes` peak-memory copy.
    with open(path, "r", encoding="latin-1", newline="") as f:
        text = f.read()

    # Anti-pattern: re-encode the whole payload back to bytes
    data = text.encode("latin-1")

    counts: dict[bytes, int] = {}
    # Anti-pattern: slice allocates a fresh `bytes` per bigram, then we use it
    # as a dict key (object hashing + bytes interning churn).
    for i in range(len(data) - 1):
        bigram = data[i : i + 2]
        if bigram in counts:
            counts[bigram] += 1
        else:
            counts[bigram] = 1
    return counts
