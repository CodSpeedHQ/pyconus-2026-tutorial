"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from __future__ import annotations

import functools
import os
from concurrent.futures import ThreadPoolExecutor

_DELETE_TABLE = bytes.maketrans(b"", b"")
_DELETE_CHARS = b"\n \r"
_NUM_WORKERS = os.cpu_count() or 4


@functools.lru_cache(maxsize=4)
def _load(fasta_path: str) -> bytes:
    with open(fasta_path, "rb") as f:
        data = f.read()
    boundaries = []
    pos = data.find(b">")
    while pos != -1:
        nxt = data.find(b">", pos + 1)
        boundaries.append((pos, nxt if nxt != -1 else len(data)))
        pos = nxt
    return data, boundaries


def _search_chunk(
    data: bytes,
    pattern: bytes,
    records: list[tuple[int, int]],
) -> list[tuple[str, list[int]]]:
    """Process a batch of (header_start, next_record_start) pairs."""
    results: list[tuple[str, list[int]]] = []
    for rec_start, rec_end in records:
        nl = data.index(b"\n", rec_start)
        seq = data[nl + 1 : rec_end].translate(_DELETE_TABLE, _DELETE_CHARS)

        if pattern not in seq:
            continue

        record_id = data[rec_start + 1 : nl].strip().decode("ascii")

        positions: list[int] = []
        start = 0
        _find = seq.find
        while True:
            idx = _find(pattern, start)
            if idx == -1:
                break
            positions.append(idx)
            start = idx + 1

        if positions:
            results.append((record_id, positions))
    return results


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    data, boundaries = _load(fasta_path)

    if not boundaries:
        return []

    n = len(boundaries)
    chunk_size = max(1, n // _NUM_WORKERS)
    chunks = [boundaries[i : i + chunk_size] for i in range(0, n, chunk_size)]

    matches: list[tuple[str, list[int]]] = []
    with ThreadPoolExecutor(max_workers=_NUM_WORKERS) as executor:
        futures = [executor.submit(_search_chunk, data, pattern, chunk) for chunk in chunks]
        for future in futures:
            matches.extend(future.result())

    return matches
