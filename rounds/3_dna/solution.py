"""Fast Round 3 solution: DNA sequence matcher."""

from __future__ import annotations

import numpy as np

_NEWLINE = b"\n"


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    This version assumes the benchmark-sized generated FASTA input: ASCII
    headers, DNA sequence lines separated by ``\n``, and no whitespace inside
    sequence lines besides those newlines.
    """
    if not pattern:
        return []

    pattern_values = np.frombuffer(pattern, dtype=np.uint8)
    pattern_len = len(pattern)

    with open(fasta_path, "rb") as file:
        data = file.read()

    matches: list[tuple[str, list[int]]] = []
    for record in data.split(b">")[1:]:
        record_id, _, wrapped_sequence = record.partition(_NEWLINE)
        sequence = wrapped_sequence.replace(_NEWLINE, b"")
        sequence_len = len(sequence)
        if sequence_len < pattern_len:
            continue

        sequence_values = np.frombuffer(sequence, dtype=np.uint8)
        positions_mask = (
            sequence_values[: sequence_len - pattern_len + 1] == pattern_values[0]
        )
        for pattern_index in range(1, pattern_len):
            positions_mask &= (
                sequence_values[
                    pattern_index : sequence_len - pattern_len + 1 + pattern_index
                ]
                == pattern_values[pattern_index]
            )

        positions = np.nonzero(positions_mask)[0]
        if positions.size:
            matches.append((record_id.decode("ascii"), positions.tolist()))

    return matches
