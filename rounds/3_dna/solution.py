"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from .baseline import find_matches as _baseline
import regex
from multiprocessing.pool import ThreadPool

def match(record, pattern_str):
    if not record.strip():
        return None, []

    # split record ID
    lines = record.split("\n")
    record_id = lines[0].strip()
    sequence = "".join(lines[1:]).replace(" ", "")

    # regex pattern match, get position if match
    match_inds = []
    for match in regex.finditer(pattern_str, sequence, overlapped=True):
        match_inds.append(match.start())
    
    return record_id, match_inds


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    results = []
    records = text.split(">")
    args = [(record, pattern_str) for record in records]

    with ThreadPool(10) as pool:

        for record_id, match_inds in pool.starmap(match, args):
            if len(match_inds) > 0:
                # append to results
                results.append((record_id, match_inds))

    return results
