"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # Step 1: read the whole file into memory as a single bytes object.
    with open(path, "rb") as f:
        data = f.read()

    # Create a 2D matrix to count bigrams
    counts = [[0] * 256 for _ in range(256)]

    for i in range(len(data) - 1):
        # Increment the count in each cell
        counts[data[i]][data[i + 1]] += 1

    # Convert the matrix to the original format
    output = {}
    for i in range(256):
        for j in range(256):
            if counts[i][j] > 0:
                output[bytes([i, j])] = counts[i][j]
    return output
