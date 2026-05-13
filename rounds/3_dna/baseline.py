"""Round 3 baseline: DNA sequence matcher.

Parses a FASTA-like file and returns every record whose nucleotide sequence
contains a given pattern, along with the positions of each occurrence.
"""

from __future__ import annotations


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # Step 1: read the whole FASTA file as text and decode the pattern so the
    # search below can use a single ``str`` API.
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    matches: list[tuple[str, list[int]]] = []

    # Step 2: split the file on '>' to peel off one record at a time. The
    # first element is the chunk before any header (empty for well-formed
    # files) and is skipped by the ``.strip()`` guard below.
    for record in text.split(">"):
        if not record.strip():
            continue

        # Step 3: a record looks like ``"<id>\n<seq line 1>\n<seq line 2>\n..."``.
        # The id is the first line; the remaining lines are joined back into a
        # single contiguous sequence string.
        lines = record.split("\n")
        record_id = lines[0].strip()
        sequence = "".join(lines[1:]).replace(" ", "")

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
