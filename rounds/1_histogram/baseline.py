"""Round 1 baseline: byte-pair histogram.

Counts the frequency of every 2-byte bigram (256 * 256 = 65,536 possible
tokens) in a binary payload.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # Step 1: read the whole file into memory as a single bytes object.
    with open(path, "rb") as f:
        data = f.read()

    # Step 2: slide a 2-byte window across the buffer. For ``b"ABCD"`` the
    # iterations produce ``b"AB"``, ``b"BC"``, then ``b"CD"``. For each window,
    # bump the matching bucket in a ``dict`` keyed by the bigram itself.
    counts: dict[bytes, int] = {}
    for i in range(len(data) - 1):
        bigram = data[i : i + 2]
        if bigram in counts:
            counts[bigram] += 1
        else:
            counts[bigram] = 1
    return counts
