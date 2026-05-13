from __future__ import annotations

import mmap
import os
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from os import PathLike
from typing import Iterator, Union


Pathish = Union[str, bytes, PathLike[str], PathLike[bytes]]

# (record_index, record_start_offset, record_end_offset)
Span = tuple[int, int, int]

# (record_index, record_id, match_positions)
SearchResult = tuple[int, str, list[int]]

# Baseline behavior removes spaces and newlines from sequence text.
# In binary mode we also remove '\r' to match text-mode universal newlines.
_DELETE_SEQUENCE_BYTES = b" \r\n"


def _default_worker_count() -> int:
    # Python 3.13+ may expose process_cpu_count(), which respects CPU limits.
    process_cpu_count = getattr(os, "process_cpu_count", None)

    if process_cpu_count is not None:
        count = process_cpu_count()
    else:
        count = os.cpu_count()

    return count or 1


def _iter_record_spans(mm: mmap.mmap, size: int) -> Iterator[Span]:
    """
    Yield FASTA record byte ranges.

    Assumes valid FASTA-style records where headers begin with '>' at the start
    of a line. This is faster than splitting the whole file on b'>'.
    """

    if size == 0:
        return

    if mm[:1] == b">":
        start = 0
    else:
        marker = mm.find(b"\n>")
        if marker < 0:
            return
        start = marker + 1

    index = 0

    while start < size:
        next_marker = mm.find(b"\n>", start + 1)
        end = size if next_marker < 0 else next_marker

        yield index, start, end

        index += 1

        if next_marker < 0:
            break

        start = next_marker + 1


def _find_overlapping_positions(sequence: bytes, pattern: bytes) -> list[int]:
    """
    Return every overlapping occurrence of pattern in sequence.

    Example:
        sequence = b"AAAA"
        pattern  = b"AA"
        result   = [0, 1, 2]
    """

    # Match the baseline's empty-pattern behavior.
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


def _search_batch(
    mm: mmap.mmap,
    spans: list[Span],
    pattern: bytes,
) -> list[SearchResult]:
    """
    Worker function.

    Each worker processes a batch of records. Batching is important for a file
    with ~10k sequences because submitting 10k individual futures is wasteful.
    """

    results: list[SearchResult] = []
    append_result = results.append
    delete_bytes = _DELETE_SEQUENCE_BYTES

    for index, start, end in spans:
        header_end = mm.find(b"\n", start, end)

        if header_end < 0:
            # Header-only record.
            record_id = mm[start + 1 : end].strip().decode("ascii")
            sequence = b""
        else:
            record_id = mm[start + 1 : header_end].strip().decode("ascii")

            # This does sequence normalization in C:
            # remove line breaks and spaces from the sequence portion.
            sequence = mm[header_end + 1 : end].translate(None, delete_bytes)

        positions = _find_overlapping_positions(sequence, pattern)
        append_result((index, record_id, positions))

    return results


def find_matches(
    fasta_path: Pathish,
    pattern: bytes,
    *,
    max_workers: int | None = None,
    batch_records: int = 128,
    batch_bytes: int = 8 << 20,  # 8 MiB
    max_pending_batches: int | None = None,
) -> list[tuple[str, list[int]]]:
    """
    Find every FASTA record whose sequence contains `pattern`.

    Returns:
        [(record_id, [positions...]), ...]

    Tuned for roughly:
        - 512 MB input
        - ~10,145 records
        - free-threaded CPython

    The defaults create approximately 60-90 tasks for your file size, rather
    than 10,145 tiny tasks.
    """

    pattern = bytes(pattern)

    # Preserve the baseline's assumption that the pattern is ASCII text.
    pattern.decode("ascii")

    if max_workers is None:
        max_workers = _default_worker_count()

    if max_workers < 1:
        raise ValueError("max_workers must be positive")

    if batch_records < 1:
        raise ValueError("batch_records must be positive")

    if batch_bytes < 1:
        raise ValueError("batch_bytes must be positive")

    if max_pending_batches is None:
        max_pending_batches = max_workers * 4

    if max_pending_batches < 1:
        raise ValueError("max_pending_batches must be positive")

    size = os.path.getsize(fasta_path)

    if size == 0:
        return []

    matches: list[tuple[str, list[int]]] = []

    # Completed records waiting to be emitted in file order.
    ready: dict[int, tuple[str, list[int]]] = {}

    next_to_emit = 0

    def collect(done: set[Future[list[SearchResult]]]) -> None:
        nonlocal next_to_emit

        for future in done:
            for index, record_id, positions in future.result():
                ready[index] = (record_id, positions)

        # Preserve file order even when worker batches complete out of order.
        while next_to_emit in ready:
            record_id, positions = ready.pop(next_to_emit)

            if positions:
                matches.append((record_id, positions))

            next_to_emit += 1

    with open(fasta_path, "rb") as file:
        with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                pending: set[Future[list[SearchResult]]] = set()

                batch: list[Span] = []
                batch_size = 0

                for span in _iter_record_spans(mm, size):
                    _, start, end = span

                    batch.append(span)
                    batch_size += end - start

                    if len(batch) >= batch_records or batch_size >= batch_bytes:
                        pending.add(executor.submit(_search_batch, mm, batch, pattern))

                        batch = []
                        batch_size = 0

                        # Backpressure. Avoid queueing unbounded work.
                        if len(pending) >= max_pending_batches:
                            done, pending = wait(
                                pending,
                                return_when=FIRST_COMPLETED,
                            )
                            collect(done)

                if batch:
                    pending.add(executor.submit(_search_batch, mm, batch, pattern))

                while pending:
                    done, pending = wait(
                        pending,
                        return_when=FIRST_COMPLETED,
                    )
                    collect(done)

    return matches
