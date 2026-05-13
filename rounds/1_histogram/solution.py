"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # TODO: remove this delegation and write your own implementation here.
    with open(path, "rb") as f:
        data = f.read()

    counts = []
    for ii in range(256):
        counts.append([])
        for jj in range(256):
            counts[ii].append(0)
            
    for ii in range(len(data) - 1):
        counts[data[ii]][data[ii+1]] += 1

    d = {}
    for rr in range(256):
        for cc in range(256):
            if counts[rr][cc] > 0:
                d[bytes((rr,cc))] = counts[rr][cc]
    return d
