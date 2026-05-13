"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""
from collections import Counter
from pathlib import Path


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # TODO: remove this delegation and write your own implementation here.
    with open(path, "rb") as file:
        data = file.read()

    counts = [[0] * 256 for _ in range(256)]
    for index in range(len(data) - 1):
        counts[data[index]][data[index + 1]] += 1

    result = {}
    x = y = 0
    while x < 256:
        item =  counts[x][y]
        if item != 0:
            result[bytes([x, y])] = counts[x][y]

        if y == 255:
            x += 1
        y = (y + 1) % 256

    return result

# DATA_DIR = Path(__file__).parent / "data"
# FIXTURE_PATH = DATA_DIR / "fixture_payload.bin"
# PAYLOAD_PATH = DATA_DIR / "payload.bin"
# result = compute_histogram(PAYLOAD_PATH)
