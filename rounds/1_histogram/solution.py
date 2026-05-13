"""Your Round 1 solution — byte-pair histogram.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``compute_histogram`` with your
own faster implementation.
"""


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    # TODO: Add comment to push to branch 
    from .baseline import compute_histogram as _baseline

    return _baseline(path)
