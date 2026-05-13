"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""

def compute_histogram(path: str) -> dict[bytes, int]:
    with open(path, "rb") as f:
        data = f.read()

    counts = {}

    for a, b in zip(data, data[1:]):
        k = (a << 8) | b
        counts[k] = counts.get(k, 0) + 1

    return {
        k.to_bytes(2, "big"): v
        for k, v in counts.items()
    }