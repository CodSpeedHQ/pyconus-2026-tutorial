"""Your Round 3 solution — DNA sequence matcher."""

from __future__ import annotations
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import mmap
import os


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # Read as bytes — no decode overhead, pattern stays as bytes.
    regex = re.compile(b"(?=" + re.escape(pattern) + b")")
    with open(fasta_path, "rb") as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            data = bytes(mm)
        size = len(data)

    # Find record boundaries without copying data
    offsets = [0]
    pos = data.find(b">", 1)
    while pos != -1:
        offsets.append(pos)
        pos = data.find(b">", pos + 1)
    offsets.append(size)

    def process_record(
        start: int, end: int, idx: int
    ) -> tuple[int, tuple[str, list[int]]] | None:
        chunk = data[start:end]
        lines = chunk.split(b"\n")
        record_id = lines[0][1:].strip().decode("ascii")
        sequence = b"".join(lines[1:]).replace(b" ", b"")
        positions = [m.start() for m in regex.finditer(sequence)]
        if positions:
            return (idx, (record_id, positions))
        return None

    max_workers = min(32, (os.cpu_count() or 1) * 2)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(process_record, offsets[i], offsets[i + 1], i)
            for i in range(len(offsets) - 1)
        ]
        results = [r for f in as_completed(futures) if (r := f.result()) is not None]

    results.sort(key=lambda x: x[0])
    return [r for _, r in results]
