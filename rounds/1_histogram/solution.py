"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""


# def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # TODO: Used chatgpt for optimization of byte-pair histogram 
   # from .baseline import compute_histogram as _baseline

    #return _baseline(path)

def histogram_dict(counts: list[int]) -> dict[bytes, int]:
    out = {}

    for i, count in enumerate(counts):
        if count:
            out[i.to_bytes(2, "big")] = count

    return out
