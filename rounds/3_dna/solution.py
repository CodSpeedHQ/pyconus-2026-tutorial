"""Your Round 3 solution — DNA sequence matcher."""

from __future__ import annotations
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    # Read as bytes — no decode overhead, pattern stays as bytes.
    with open(fasta_path, "rb") as f:
        data = f.read()

    # Pre-compile a lookahead regex so overlapping matches are found in one pass.
    regex = re.compile(b"(?=" + re.escape(pattern) + b")")

    def process_record(record: bytes) -> tuple[str, list[int]] | None:
        if not record.strip():
            return None
        lines = record.split(b"\n")
        record_id = lines[0].strip().decode("ascii")
        sequence = b"".join(lines[1:]).replace(b" ", b"")
        positions = [m.start() for m in regex.finditer(sequence)]
        if positions:
            return (record_id, positions)
        return None

    # Split on b'>' — first chunk is empty for well-formed files.
    records = data.split(b">")[1:]  # skip leading empty chunk

    results: list[tuple[str, list[int]]] = []

    # re operations release the GIL, so ThreadPoolExecutor gives real parallelism.
    with ThreadPoolExecutor() as executor:
        # Submit in order, preserve file order via index.
        futures = {executor.submit(process_record, r): i for i, r in enumerate(records)}
        ordered: list[tuple[int, tuple[str, list[int]]]] = []
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                ordered.append((futures[future], result))

    ordered.sort(key=lambda x: x[0])
    results = [r for _, r in ordered]
    return results
