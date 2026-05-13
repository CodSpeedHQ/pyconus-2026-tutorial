"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from concurrent.futures import ThreadPoolExecutor


def _find_matches(pattern_str: str, record: str) -> tuple[str, list[int]]:
    lines = record.split("\n")
    record_id = lines[0].strip()
    sequence = "".join(lines[1:]).replace(" ", "")

    positions: list[int] = []
    start = 0
    while True:
        pos = sequence.find(pattern_str, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1

    return (record_id, positions)


def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    pattern_str = pattern.decode("ascii")
    matches = []
    with open(fasta_path, "r") as f:
        text = f.read()

    with ThreadPoolExecutor(16) as ex:
        futures = [
            ex.submit(_find_matches, pattern_str, record)
            for record in text.split(">")
            if record.strip()
        ]
        matches = [res for future in futures if (res := future.result())[1]]
    return matches
