"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

import re
import string
from concurrent.futures import ThreadPoolExecutor

table = bytes.maketrans(b"", b"")

def find_match(args):
        pattern_str,record = args
        # Step 3: a record looks like ``"<id>\n<seq line 1>\n<seq line 2>\n..."``.
        # The id is the first line; the remaining lines are joined back into a
        # single contiguous sequence string.
        lines = record.split(b'\n', 1)
        record_id = lines[0].strip()
        sequence_raw = lines[1]
        sequence = sequence_raw.translate(table, delete=string.whitespace.encode())

        positions: list[int] = []
        start = 0
        while True:
            pos = sequence.find(pattern_str, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1

        if positions:
            return (record_id.decode('ascii'), positions)
        else:
            return None


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # TODO: remove this delegation and write your own implementation here.
    # Step 1: read the whole FASTA file as text and decode the pattern so the
    # search below can use a single ``str`` API.
    with open(fasta_path, "rb") as f:
        text = f.read()

    matches: list[tuple[str, list[int]]] = []

    with ThreadPoolExecutor() as ex:
        futures = []
        for record in text.split(b">"):
            if not record.strip():
                continue

            t = ex.submit(find_match, args=(pattern,record))
            futures.append(t)
    
        for t in futures:
            result = t.result()
            if result:
                matches.append(result)
    return matches
