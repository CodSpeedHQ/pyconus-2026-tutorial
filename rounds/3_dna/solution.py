from __future__ import annotations

import os
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from os import PathLike
from typing import Iterator, Union


Pathish = Union[str, bytes, PathLike[str], PathLike[bytes]]

Record = tuple[int, str, bytearray]
SearchResult = tuple[int, str, list[int]]


def _iter_fasta_records(fasta_path: Pathish) -> Iterator[Record]:
    """
    Yield FASTA records as:

        (record_index, record_id, sequence)

    The sequence is accumulated as bytes, with literal spaces removed to match
    the baseline behavior.
    """

    record_id: str | None = None
    sequence = bytearray()
    index = 0

    with open(fasta_path, "rb") as f:
        for raw_line in f:
            if raw_line[:1] == b">":
                if record_id is not None:
                    yield index, record_id, sequence
                    index += 1

                record_id = raw_line[1:].strip().decode("ascii")
                sequence = bytearray()
                continue

            # Ignore preamble before the first FASTA header.
            if record_id is None:
                continue

            line = raw_line.rstrip(b"\r\n")

            # Match the baseline's `.replace(" ", "")`.
            if b" " in line:
                line = line.replace(b" ", b"")

            sequence.extend(line)

    if record_id is not None:
        yield index, record_id, sequence


def _find_overlapping_positions(sequence: bytearray, pattern: bytes) -> list[int]:
    """
    Find all overlapping occurrences of pattern in sequence.

    Example:
        sequence = b"AAAA"
        pattern  = b"AA"
        result   = [0, 1, 2]
    """

    # Preserve baseline behavior:
    # an empty pattern matches every position from 0 through len(sequence).
    if not pattern:
        return list(range(len(sequence) + 1))

    positions: list[int] = []
    append = positions.append
    find = sequence.find

    start = 0

    while True:
        pos = find(pattern, start)
        if pos < 0:
            return positions

        append(pos)
        start = pos + 1


def _search_batch(batch: list[Record], pattern: bytes) -> list[SearchResult]:
    """
    Worker function.

    Each worker receives a batch of records to reduce ThreadPoolExecutor
    scheduling overhead for FASTA files with many small records.
    """

    return [
        (index, record_id, _find_overlapping_positions(sequence, pattern))
        for index, record_id, sequence in batch
    ]


def find_matches(
    fasta_path: Pathish,
    pattern: bytes,
    *,
    max_workers: int | None = None,
    max_pending_batches: int | None = None,
    batch_records: int = 64,
    batch_bytes: int = 8 << 20,  # 8 MiB of sequence data
) -> list[tuple[str, list[int]]]:
    """
    Find every FASTA record whose sequence contains `pattern`.

    Returns:
        [(record_id, [positions...]), ...]

    Threaded design:
    - main thread parses the FASTA file
    - worker threads search records in parallel
    - main thread collects results and emits them in original file order

    This is designed for free-threaded Python. On normal GIL-enabled CPython,
    CPU-bound speedup may be much smaller.
    """

    pattern = bytes(pattern)

    if max_workers is None:
        max_workers = os.cpu_count() or 1
    if max_workers < 1:
        raise ValueError("max_workers must be positive")

    if max_pending_batches is None:
        max_pending_batches = max_workers * 2
    if max_pending_batches < 1:
        raise ValueError("max_pending_batches must be positive")

    if batch_records < 1:
        raise ValueError("batch_records must be positive")
    if batch_bytes < 1:
        raise ValueError("batch_bytes must be positive")

    matches: list[tuple[str, list[int]]] = []

    # Completed records waiting to be emitted in file order.
    ready: dict[int, tuple[str, list[int]]] = {}

    pending: set[Future[list[SearchResult]]] = set()
    next_to_emit = 0

    def collect(done: set[Future[list[SearchResult]]]) -> None:
        nonlocal next_to_emit

        for future in done:
            for index, record_id, positions in future.result():
                ready[index] = (record_id, positions)

        # Emit only when the next file-order record is available.
        while next_to_emit in ready:
            record_id, positions = ready.pop(next_to_emit)

            if positions:
                matches.append((record_id, positions))

            next_to_emit += 1

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        batch: list[Record] = []
        batch_size = 0

        for record in _iter_fasta_records(fasta_path):
            batch.append(record)
            batch_size += len(record[2])

            if len(batch) >= batch_records or batch_size >= batch_bytes:
                pending.add(executor.submit(_search_batch, batch, pattern))
                batch = []
                batch_size = 0

                # Backpressure: do not let the parser enqueue the whole file.
                if len(pending) >= max_pending_batches:
                    done, pending = wait(pending, return_when=FIRST_COMPLETED)
                    collect(done)

        if batch:
            pending.add(executor.submit(_search_batch, batch, pattern))

        while pending:
            done, pending = wait(pending, return_when=FIRST_COMPLETED)
            collect(done)

    return matches
