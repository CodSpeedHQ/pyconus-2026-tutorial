"""Round 1 baseline: byte-pair histogram.

Counts the frequency of every 2-byte bigram (256 * 256 = 65,536 possible
tokens) in a binary payload.
"""

from pathlib import Path

# -------------------------------------------------------------------------------------------------

def compute_histogram(path):
    """Return frequency of every 2-byte bigram in the file at path."""
    counts = [0] * 65536
    previous = None

    with Path(path).open("rb") as file:
        while chunk := file.read(1024 * 1024):
            for byte in chunk:
                if previous is not None:
                    counts[(previous << 8) | byte] += 1
                previous = byte

    return {
        bigram.to_bytes(2, "big"): count
        for bigram, count in enumerate(counts)
        if count
    }
