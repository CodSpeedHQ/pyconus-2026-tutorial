"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from .baseline import find_matches as _baseline


def find_record_matches(pattern_str, sequence):
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
    return positions

def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # Step 1: read the whole FASTA file as text and decode the pattern so the
    # search below can use a single ``str`` API.
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    # Step 2: split the file on '>' to peel off one record at a time. The
    # first element is the chunk before any header (empty for well-formed
    # files) and is skipped by the ``.strip()`` guard below.

    futures = {}

    with ThreadPoolExecutor(max_workers=None) as executor:

        for record in text.split(">"):
            if not record.strip():
                continue

            # Step 3: a record looks like ``"<id>\n<seq line 1>\n<seq line 2>\n..."``.
            # The id is the first line; the remaining lines are joined back into a
            # single contiguous sequence string.
            lines = record.split("\n")
            record_id = lines[0].strip()
            sequence = "".join(lines[1:]).replace(" ", "")

            futures[executor.submit(find_record_matches, pattern_str, sequence)] = record_id


    return [
        (record_id, positions)
        for future, record_id in futures.items()
        if (positions := future.result())
    ]
