"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from concurrent.futures import ThreadPoolExecutor
from threading import Thread


def find_matches_in_sequence(
    record_id: str,
    sequence: str,
    pattern_str: str,
    matches: list[tuple[str, list[int]]],
):
    """Find matches in a single sequence and append to the shared matches list."""
    positions: list[int] = []
    start = 0
    while True:
        pos = sequence.find(pattern_str, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1

    if positions:
        matches.append((record_id, positions))


def find_matches_many_threads(
    fasta_path: str, pattern: bytes
) -> list[tuple[str, list[int]]]:
    # Step 1: read the whole FASTA file as text and decode the pattern so the
    # search below can use a single ``str`` API.
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    matches: list[tuple[str, list[int]]] = []

    # Preprocess the sequences
    sequences = []
    for record in text.split(">"):
        if not record.strip():
            continue
        lines = record.split("\n")
        record_id = lines[0].strip()
        sequence = "".join(lines[1:]).replace(" ", "")
        sequences.append((record_id, sequence))
    threads = []
    for record_id, sequence in sequences:
        thread = Thread(
            target=find_matches_in_sequence,
            args=(record_id, sequence, pattern_str, matches),
        )
        thread.start()
        threads.append(thread)
    # Wait for all threads to finish
    print(f"Waiting for {len(threads)} threads to finish...")
    for thread in threads:
        thread.join()

    return matches


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    # Step 1: read the whole FASTA file as text and decode the pattern so the
    # search below can use a single ``str`` API.
    pattern_str = pattern.decode("ascii")
    with open(fasta_path, "r") as f:
        text = f.read()

    matches: list[tuple[str, list[int]]] = []

    # Preprocess the sequences
    sequences = []
    for record in text.split(">"):
        if not record.strip():
            continue
        lines = record.split("\n")
        record_id = lines[0].strip()
        sequence = "".join(lines[1:]).replace(" ", "")
        sequences.append((record_id, sequence))

    # Create a pool of threads
    pool = ThreadPoolExecutor(max_workers=len(sequences))
    for record_id, sequence in sequences:
        pool.submit(
            find_matches_in_sequence,
            record_id,
            sequence,
            pattern_str,
            matches,
        )
    # Wait for all threads to finish
    pool.shutdown(wait=True)

    return matches
