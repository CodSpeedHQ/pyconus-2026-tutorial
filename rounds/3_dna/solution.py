"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from __future__ import annotations


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # Read as bytes — skips the text-decode cost the baseline pays.
    with open(fasta_path, "rb") as f:
        data = f.read()

    plen = len(pattern)
    _find = bytes.find  # local lookup
    matches: list[tuple[str, list[int]]] = []

    # Skip the first (empty) chunk before the first ">".
    for record in data.split(b">")[1:]:
        # Header ends at the first newline.
        nl = record.index(b"\n")
        # Build the contiguous sequence by stripping newlines — a single
        # C-level bytes.replace() call instead of split-then-join.
        sequence = record[nl + 1 :].replace(b"\n", b"")

        # Quick exit: most records do not contain the pattern at all.
        # ``in`` delegates to a fast C memchr/memmem scan.
        pos = _find(sequence, pattern)
        if pos == -1:
            continue

        record_id = record[:nl].strip().decode("ascii")

        # Collect all (overlapping) hit positions.
        positions: list[int] = [pos]
        start = pos + 1
        while True:
            pos = _find(sequence, pattern, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        matches.append((record_id, positions))

    return matches
