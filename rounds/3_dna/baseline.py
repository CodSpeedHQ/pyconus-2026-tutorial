"""Round 3 baseline — DNA sequence matcher.

Parses a FASTA-like file and returns every record whose nucleotide sequence
contains a given pattern, along with the positions of each occurrence.
"""

from __future__ import annotations


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    matches: list[tuple[str, list[int]]] = []
    for record in text.split(">"):
        if not record.strip():
            continue
        lines = record.split("\n")
        record_id = lines[0].strip()
        sequence = "".join(lines[1:]).replace(" ", "")

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
