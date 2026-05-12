"""Your Round 2 solution — corruption scanner.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_corruptions`` with your
own faster implementation.
"""

from .baseline import find_corruptions as _baseline


def find_corruptions(ref_path: str, cor_path: str) -> list[tuple[int, int]]:
    """Return ``[(offset, length), ...]`` for every differing byte range."""
    # TODO: remove this delegation and write your own implementation here.
    return _baseline(ref_path, cor_path)
