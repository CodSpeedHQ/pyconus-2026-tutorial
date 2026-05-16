"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """

    results = []

    current_id = None
    chunks = []

    with open(fasta_path, "rb") as f:
        for line in f:
            line = line.rstrip(b"\n")

            if line.startswith(b">"):
                if current_id is not None:
                    seq = b"".join(chunks)
                    positions = find_all(seq, pattern)

                    if positions:
                        results.append((current_id, positions))

                current_id = line[1:].decode("ascii")
                chunks = []

            else:
                chunks.append(line)

        if current_id is not None:
            seq = b"".join(chunks)
            positions = find_all(seq, pattern)

            if positions:
                results.append((current_id, positions))

    return results


def find_all(seq: bytes, pattern: bytes) -> list[int]:
    positions = []
    start = 0

    while True:
        pos = seq.find(pattern, start)

        if pos == -1:
            break

        positions.append(pos)
        start = pos + 1

    return positions