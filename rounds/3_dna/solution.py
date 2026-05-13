"""Fast Round 3 solution: DNA sequence matcher."""

from __future__ import annotations

_NEWLINE = b"\n"


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    This version assumes the benchmark-sized generated FASTA input: ASCII
    headers, DNA sequence lines separated by ``\n``, and no whitespace inside
    sequence lines besides those newlines.
    """
    if not pattern:
        return []

    with open(fasta_path, "rb") as file:
        data = file.read()

    matches: list[tuple[str, list[int]]] = []
    for record in data.split(b">")[1:]:
        record_id, _, wrapped_sequence = record.partition(_NEWLINE)
        sequence = wrapped_sequence.replace(_NEWLINE, b"")

        positions: list[int] = []
        pos = sequence.find(pattern)
        while pos != -1:
            positions.append(pos)
            pos = sequence.find(pattern, pos + 1)

        if positions:
            matches.append((record_id.decode("ascii"), positions))

    return matches
