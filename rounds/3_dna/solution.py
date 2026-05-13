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
    with open(fasta_path, "rb") as f:
        text = f.read()

    matches: list[tuple[str, list[int]]] = []

    for record in text.split(b">"):
        if not record.strip():
            continue

        lines = record.split(b"\n")
        record_id = lines[0].strip().decode("ascii")
        sequence = b"".join(lines[1:]).replace(b" ", b"")

        positions: list[int] = []
        start = 0
        while True:
            pos = sequence.find(pattern, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        if positions:
            matches.append((record_id, positions))

    return matches
