"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

_NL = 0x0A  # b"\n"


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    with open(fasta_path, "rb") as f:
        data = f.read()

    # Step 1: locate every record start. A record starts with ``>`` either at
    # offset 0 or immediately after a ``\n``.
    starts: list[int] = []
    i = 0
    while True:
        p = data.find(b">", i)
        if p == -1:
            break
        if p == 0 or data[p - 1] == _NL:
            starts.append(p)
        i = p + 1
    starts.append(len(data))  # sentinel marking the end of the last record.

    num_records = len(starts) - 1
    if num_records <= 0:
        return []

    # Step 2: parallel scan. Choose enough batches to keep workers balanced
    # even when record sizes vary.
    n_workers = max(1, os.cpu_count() or 1)
    batches = max(1, n_workers * 4)
    batch_size = max(1, (num_records + batches - 1) // batches)

    def scan_batch(start_idx: int, end_idx: int) -> list[tuple[int, str, list[int]]]:
        out: list[tuple[int, str, list[int]]] = []
        for j in range(start_idx, end_idx):
            rec_start = starts[j]
            rec_end = starts[j + 1]

            # Locate the end of the header line within this record's slice.
            nl = data.find(b"\n", rec_start, rec_end)
            if nl <= rec_start:
                continue  # Malformed or header-only.

            record_id = data[rec_start + 1 : nl].decode("ascii").strip()

            # Contiguous sequence: drop the newlines so matches that straddle
            # line breaks are still found by ``bytes.find``.
            sequence = data[nl + 1 : rec_end].replace(b"\n", b"")

            positions: list[int] = []
            s = 0
            while True:
                p = sequence.find(pattern, s)
                if p == -1:
                    break
                positions.append(p)
                s = p + 1

            if positions:
                out.append((j, record_id, positions))
        return out

    with ThreadPoolExecutor(max_workers=n_workers) as pool:
        futures = [
            pool.submit(scan_batch, lo, min(lo + batch_size, num_records))
            for lo in range(0, num_records, batch_size)
        ]
        chunks = [f.result() for f in futures]

    # Step 3: flatten and restore file order (record index is monotonic per
    # batch, but batches finish in arbitrary order).
    flat = [item for chunk in chunks for item in chunk]
    flat.sort(key=lambda triple: triple[0])
    return [(rid, positions) for _, rid, positions in flat]
