"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from mmap import ACCESS_READ, mmap
from os import fstat

_NUM_WORKERS = os.cpu_count() or 4


def _scan_record(record: bytes, pattern: bytes) -> tuple[str, list[int]] | None:
    """Scan one FASTA record for all occurrences of ``pattern``.

    Returns the record id and every zero-based match position, or ``None`` if
    the record is empty or does not contain the pattern.
    """

    if not record.strip():
        return None

    # Parition DNA record into header and DNA sequence
    header, _, body = record.partition(b"\n")
    record_id = header.strip().decode("ascii")

    # Clean up data before parsing
    sequence = body.replace(b"\n", b"").replace(b"\r", b"").replace(b" ", b"")

    positions: list[int] = []
    start = 0

    # Advance by one after each hit so overlapping matches are included.
    while True:
        pos = sequence.find(pattern, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1

    if not positions:
        return None

    return record_id, positions


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    with open(fasta_path, "rb") as f:
        if fstat(f.fileno()).st_size == 0:
            return []

        with mmap(f.fileno(), 0, access=ACCESS_READ) as text:
            # Read the file as an mmap and break it up into DNA records
            records: list[bytes] = []
            start = text.find(b">")
            while start != -1:
                end = text.find(b">", start + 1)
                if end == -1:
                    record = text[start + 1 :]
                    start = -1
                else:
                    record = text[start + 1 : end]
                    start = end

                if record.strip():
                    records.append(record)

            with ThreadPoolExecutor(max_workers=_NUM_WORKERS) as executor:
                results = executor.map(lambda record: _scan_record(record, pattern), records)

    return [result for result in results if result is not None]
