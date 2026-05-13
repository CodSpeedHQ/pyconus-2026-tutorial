"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from .baseline import find_matches as _baseline
from concurrent.futures import ThreadPoolExecutor
import threading

def _thread_worker(pattern_str: str, record: str, matches, lock:threading.Lock):
    if not record.strip():
        return
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
        with lock:
            matches[record_id] = positions

def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    matches: dict[str, list[int]] = {}

    lock = threading.Lock()
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda args: _thread_worker(*args),
                     [
                         (pattern_str, record, matches, lock)
                         for record in text.split(">")
                     ])
    matches = dict(sorted(matches.items()))
    return [(k,v) for k,v in matches.items()]