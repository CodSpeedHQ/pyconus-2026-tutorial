"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from concurrent.futures import ThreadPoolExecutor


def _scan_record(record: bytes, pattern: bytes) -> tuple[str, list[int]] | None:
    """ Scan one FASTA record for all occurrences of ``pattern``.

    Returns the record id and every zero-based match position, or ``None`` if
    the record is empty or does not contain the pattern.
    """

    if not record.strip():
        return None

    # Parition DNA record into header and DNA sequence
    header, _, body = record.partition(b'\n')
    record_id = header.strip().decode('ascii')

    # Keep the hot path in bytes so we avoid decoding each whole sequence.
    # Whitespace is not part of the DNA sequence, so remove it before scanning.
    sequence = (
        body.replace(b'\n', b'')
            .replace(b'\r', b'')
            .replace(b' ', b'')
    )

    positions: list[int] = []
    start = 0

    # Advance by one after each hit so overlapping matches are included.
    while True:
        pos = sequence.find(pattern, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1

    if not positions:
        return None

    return record_id, positions


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """

    # Read once in binary mode so parsing and searching can stay on bytes.
    with open(fasta_path, 'rb') as f:
        text = f.read()

    # Split into DNA sequences
    records = [record for record in text.split(b'>') if record.strip()]

    # Scan records concurrently
    with ThreadPoolExecutor() as executor:
        results = executor.map(lambda record: _scan_record(record, pattern), records)

    return [result for result in results if result is not None]
