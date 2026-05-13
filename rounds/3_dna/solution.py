"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""
import os
from concurrent.futures import ThreadPoolExecutor


def _find_record_matches(pattern, sequence):
    positions: list[int] = []
    start = 0
    while True:
        pos = sequence.find(pattern, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


def _search_chunk(fasta_path, chunk_start, chunk_end, pattern):
    with open(fasta_path, "rb") as f:
        f.seek(chunk_start)
        if chunk_end is None:
            text = f.read()
        else:
            # One bulk read for the chunk, then a few readline() calls to
            # complete the last record that extends past our boundary.
            # Collect parts in a list to avoid O(n²) bytes concatenation.
            parts = [f.read(chunk_end - chunk_start)]
            while True:
                line = f.readline()
                if not line or line.startswith(b">"):
                    break
                parts.append(line)
            text = b"".join(parts)

    # For chunks that don't start at byte 0, skip the partial-record fragment
    # at the front (bytes belonging to the previous chunk's last record).
    if chunk_start > 0:
        if not text.startswith(b">"):
            idx = text.find(b"\n>")
            if idx == -1:
                return []
            text = text[idx + 1:]  # keep the ">"

    results = []
    for record in text.split(b">"):
        if not record.strip():
            continue
        lines = record.split(b"\n")
        record_id = lines[0].strip().decode("ascii")
        sequence = b"".join(lines[1:]).replace(b" ", b"")
        positions = _find_record_matches(pattern, sequence)
        if positions:
            results.append((record_id, positions))
    return results


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    num_threads = os.cpu_count() or 4
    file_size = os.path.getsize(fasta_path)
    chunk_size = max(1, file_size // num_threads)

    chunks = [
        (i * chunk_size, (i + 1) * chunk_size if i < num_threads - 1 else None)
        for i in range(num_threads)
    ]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [
            executor.submit(_search_chunk, fasta_path, start, end, pattern)
            for start, end in chunks
        ]

    results = []
    for future in futures:
        results.extend(future.result())
    return results
