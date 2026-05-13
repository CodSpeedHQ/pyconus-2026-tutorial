"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from __future__ import annotations

def _find_positions(sequence: bytes, pattern: bytes) -> list[int]:
    positions = []
    start = 0
    find = sequence.find

    while True:
        pos = find(pattern, start)

        if pos == -1:
            break

        positions.append(pos)
        start = pos + 1

    return positions


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    matches: list[tuple[str, list[int]]] = []

    with open(fasta_path, "rb") as f:
        record_id = None
        seq_parts = []

        for line in f:

            if line.startswith(b">"):

                # process previous record
                if record_id is not None:
                    sequence = b"".join(seq_parts)

                    positions = _find_positions(sequence, pattern)

                    if positions:
                        matches.append((record_id, positions))

                # begin new FASTA record
                record_id = line[1:].strip().decode("ascii")
                seq_parts = []

            else:
                seq_parts.append(line.strip())

        # process final record
        if record_id is not None:
            sequence = b"".join(seq_parts)

            positions = _find_positions(sequence, pattern)

            if positions:
                matches.append((record_id, positions))

    return matches
