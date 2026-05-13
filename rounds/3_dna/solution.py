"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Iterable


def _search_record(
    item: tuple[int, str, str],
    pattern: str,
) -> tuple[int, str, list[int]] | None:
    """
    Search one FASTA record.

    Returns:
        (original_index, record_id, positions)
        or None if no matches.
    """
    index, record_id, sequence = item

    positions: list[int] = []
    start = 0

    while True:
        pos = sequence.find(pattern, start)
        if pos == -1:
            break

        positions.append(pos)

        # advance by 1 so overlapping matches count
        start = pos + 1

    if positions:
        return (index, record_id, positions)

    return None


def _parse_fasta(path: str) -> Iterable[tuple[int, str, str]]:
    """
    Stream FASTA records one at a time.

    Yields:
        (record_index, record_id, sequence)
    """
    with open(path, "r") as f:
        record_id = None
        seq_parts: list[str] = []
        index = 0

        for line in f:
            line = line.strip()

            if not line:
                continue

            if line.startswith(">"):
                # emit previous record
                if record_id is not None:
                    yield (
                        index,
                        record_id,
                        "".join(seq_parts),
                    )
                    index += 1

                record_id = line[1:].strip()
                seq_parts = []

            else:
                seq_parts.append(line)

        # emit final record
        if record_id is not None:
            yield (
                index,
                record_id,
                "".join(seq_parts),
            )


def find_matches(
    fasta_path: str,
    pattern: bytes,
) -> list[tuple[str, list[int]]]:
    """
    Find every FASTA record whose sequence contains pattern.

    Returns:
        [(record_id, [positions...]), ...]
    """
    pattern_str = pattern.decode("ascii")

    results: list[tuple[int, str, list[int]]] = []

    # free-threaded Python can actually parallelize this
    with ThreadPoolExecutor() as pool:

        futures = [
            pool.submit(_search_record, record, pattern_str)
            for record in _parse_fasta(fasta_path)
        ]

        for future in futures:
            result = future.result()

            if result is not None:
                results.append(result)

    # preserve FASTA file order
    results.sort(key=lambda x: x[0])

    return [
        (record_id, positions)
        for _, record_id, positions in results
    ]