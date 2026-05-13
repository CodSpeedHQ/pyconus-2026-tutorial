"""Fast Round 3 solution: DNA sequence matcher."""

from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np

_NEWLINE = b"\n"


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``."""
    if not pattern:
        return []

    pattern_len = len(pattern)
    pattern_value = np.frombuffer(pattern, dtype=np.uint64)[0]

    with open(fasta_path, "rb") as file:
        data = file.read()

    records = data.split(b">")[1:]
    worker_count = os.cpu_count()

    chunk_size = (len(records) + worker_count - 1) // worker_count
    chunks = [
        records[start : start + chunk_size]
        for start in range(0, len(records), chunk_size)
    ]
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        groups = executor.map(
            _scan_records,
            chunks,
            [pattern_value] * len(chunks),
            [pattern_len] * len(chunks),
        )

    return [match for group in groups for match in group]


def _scan_records(
    records: list[bytes],
    pattern_value: np.uint64,
    pattern_len: int,
) -> list[tuple[str, list[int]]]:
    matches: list[tuple[str, list[int]]] = []
    for record in records:
        match = _scan_record(record, pattern_value, pattern_len)
        if match is not None:
            matches.append(match)
    return matches


def _scan_record(
    record: bytes,
    pattern_value: np.uint64,
    pattern_len: int,
) -> tuple[str, list[int]] | None:
    record_id, _, wrapped_sequence = record.partition(_NEWLINE)
    sequence = wrapped_sequence.replace(_NEWLINE, b"")
    sequence_len = len(sequence)
    if sequence_len < pattern_len:
        return None

    windows = np.ndarray(
        shape=(sequence_len - pattern_len + 1,),
        dtype=np.uint64,
        buffer=sequence,
        strides=(1,),
    )
    positions = np.nonzero(windows == pattern_value)[0]
    if positions.size:
        return record_id.decode("ascii"), positions.tolist()
    return None
