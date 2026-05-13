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

    pattern_len = len(pattern)
    pattern_prefix = np.frombuffer(pattern[:4], dtype=np.uint32)[0]
    pattern_suffix = np.frombuffer(pattern[4:], dtype=np.uint32)[0]

    with open(fasta_path, "rb") as file:
        data = file.read()

    records = data.split(b">")[1:]
    worker_count = min(_MAX_WORKERS, os.cpu_count() or 1, len(records))
    if worker_count <= 1:
        return _scan_records(records, pattern_prefix, pattern_suffix, pattern_len)

    chunk_size = (len(records) + worker_count - 1) // worker_count
    chunks = [
        records[start : start + chunk_size]
        for start in range(0, len(records), chunk_size)
    ]
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        groups = executor.map(
            _scan_records,
            chunks,
            [pattern_prefix] * len(chunks),
            [pattern_suffix] * len(chunks),
            [pattern_len] * len(chunks),
        )

    return [match for group in groups for match in group]


def _scan_records(
    records: list[bytes],
    pattern_prefix: np.uint32,
    pattern_suffix: np.uint32,
    pattern_len: int,
) -> list[tuple[str, list[int]]]:
    matches: list[tuple[str, list[int]]] = []
    for record in records:
        match = _scan_record(record, pattern_prefix, pattern_suffix, pattern_len)
        if match is not None:
            matches.append(match)
    return matches


def _scan_record(
    record: bytes,
    pattern_prefix: np.uint32,
    pattern_suffix: np.uint32,
    pattern_len: int,
) -> tuple[str, list[int]] | None:
    record_id, _, wrapped_sequence = record.partition(_NEWLINE)
    sequence = wrapped_sequence.replace(_NEWLINE, b"")
    sequence_len = len(sequence)
    if sequence_len < pattern_len:
        return None

    candidate_count = sequence_len - pattern_len + 1
    prefixes = np.ndarray(
        shape=(candidate_count,),
        dtype=np.uint32,
        buffer=sequence,
        strides=(1,),
    )
    candidates = np.nonzero(prefixes == pattern_prefix)[0]
    if not candidates.size:
        return None

    suffixes = np.ndarray(
        shape=(candidate_count,),
        dtype=np.uint32,
        buffer=memoryview(sequence)[4:],
        strides=(1,),
    )
    positions = candidates[suffixes[candidates] == pattern_suffix]
    if positions.size:
        return record_id.decode("ascii"), positions.tolist()
    return None
