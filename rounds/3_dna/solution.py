"""Fast Round 3 solution: DNA sequence matcher."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np

_NEWLINE = b"\n"
_MAX_WORKERS = 12


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``."""
    if not pattern:
        return []

    pattern_values = np.frombuffer(pattern, dtype=np.uint8)
    pattern_len = len(pattern)

    with open(fasta_path, "rb") as file:
        data = file.read()

    records = data.split(b">")[1:]
    worker_count = min(_MAX_WORKERS, os.cpu_count() or 1, len(records))
    if worker_count <= 1:
        return _scan_records(records, pattern_values, pattern_len)

    chunk_size = (len(records) + worker_count - 1) // worker_count
    chunks = [
        records[start : start + chunk_size]
        for start in range(0, len(records), chunk_size)
    ]
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        groups = executor.map(
            _scan_records,
            chunks,
            [pattern_values] * len(chunks),
            [pattern_len] * len(chunks),
        )

    return [match for group in groups for match in group]


def _scan_records(
    records: list[bytes], pattern_values: np.ndarray, pattern_len: int
) -> list[tuple[str, list[int]]]:
    matches: list[tuple[str, list[int]]] = []
    for record in records:
        match = _scan_record(record, pattern_values, pattern_len)
        if match is not None:
            matches.append(match)
    return matches


def _scan_record(
    record: bytes, pattern_values: np.ndarray, pattern_len: int
) -> tuple[str, list[int]] | None:
    record_id, _, wrapped_sequence = record.partition(_NEWLINE)
    sequence = wrapped_sequence.replace(_NEWLINE, b"")
    sequence_len = len(sequence)
    if sequence_len < pattern_len:
        return None

    sequence_values = np.frombuffer(sequence, dtype=np.uint8)
    candidate_count = sequence_len - pattern_len + 1
    positions_mask = sequence_values[:candidate_count] == pattern_values[0]
    for pattern_index in range(1, pattern_len):
        positions_mask &= (
            sequence_values[pattern_index : candidate_count + pattern_index]
            == pattern_values[pattern_index]
        )

    positions = np.nonzero(positions_mask)[0]
    if positions.size:
        return record_id.decode("ascii"), positions.tolist()
    return None
