"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

import re

def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # TODO: remove this delegation and write your own implementation here.
    # Step 1: read the whole FASTA file as text and decode the pattern so the
    # search below can use a single ``str`` API.
    with open(fasta_path, "r") as f:
        text = f.read()

    matches: list[tuple[str, list[int]]] = []
    pattern_str = pattern.decode('ascii')
    regex = re.compile(pattern_str)

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

        positions: list[int] = []
        positions = [m.start() for m in regex.finditer(sequence)]
        if positions:
            matches.append((record_id, positions))
    return matches
