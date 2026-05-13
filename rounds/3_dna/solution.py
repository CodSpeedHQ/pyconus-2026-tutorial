"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from .baseline import find_matches as _baseline
from threading import Thread
import numpy as np


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # Step 1: read the whole FASTA file as text and decode the pattern so the
    # search below can use a single ``str`` API.
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "rb") as f:
        text = f.read()
    matches: list[tuple[str, list[int]]] = []

    # Step 2: split the file on '>' to peel off one record at a time. The
    # first element is the chunk before any header (empty for well-formed
    # files) and is skipped by the ``.strip()`` guard below.
    for record in text.split(b">"):
        if not record.strip():
            continue

        # Step 3: a record looks like ``"<id>\n<seq line 1>\n<seq line 2>\n..."``.
        # The id is the first line; the remaining lines are joined back into a
        # single contiguous sequence string.
        lines = record.split(b"\n")
        record_id = lines[0].strip().decode("ascii")
        sequence = b"".join(lines[1:]).replace(b" ", b"").decode("ascii")

        # Step 4: walk the sequence with ``str.find()``, advancing one byte
        # past each hit so overlapping matches are reported too.
        positions: list[int] = []
        start = 0
        while True:
            pos = sequence.find(pattern_str, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        if positions:
            matches.append((record_id, positions))
    return matches
