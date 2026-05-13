"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from .baseline import find_matches as _baseline


def _process_record(record: str, pattern_str: str) -> tuple[str, list[int]] | None:
    if not record.strip():
        return None

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
        return (record_id, positions)
    return None


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:

    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    records = [record for record in text.split(">") if record.strip()]
    matches: list[tuple[str, list[int]]] = []

    with ThreadPoolExecutor(max_workers=16) as executor:
        for result in executor.map(_process_record, records, repeat(pattern_str)):
            if result:
                matches.append(result)

    return matches

