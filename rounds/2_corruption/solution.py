"""Your Round 2 solution — corruption scanner.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_corruptions`` with your
own faster implementation.
"""

from concurrent.futures import ThreadPoolExecutor


def compare_bytes(ref: bytes, cor: bytes, offset: int) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    for i in range(len(ref)):
        if ref[i] != cor[i]:
            if start is None:
                start = i
        elif start is not None:
            ranges.append((start + offset, i - start))
            start = None
    if start is not None:
        ranges.append((start + offset, len(ref) - start))
    return ranges


def find_corruptions(ref_path: str, cor_path: str) -> list[tuple[int, int]]:
    """Return ``[(offset, length), ...]`` for every differing byte range."""
    # Step 1: read both files fully into memory as bytes objects.
    with open(ref_path, "rb") as f:
        ref = f.read()
    with open(cor_path, "rb") as f:
        cor = f.read()
    if len(ref) != len(cor):
        raise ValueError("reference and corrupted files differ in length")

    N = 16
    chunk_size = len(ref) // N

    with ThreadPoolExecutor(N) as ex:
        futures = [
            ex.submit(
                compare_bytes,
                ref[i * chunk_size : (i + 1) * chunk_size],
                cor[i * chunk_size : (i + 1) * chunk_size],
                i * chunk_size,
            )
            for i in range(N)
        ]
        results = [future.result() for future in futures]

    ranges: list[tuple[int, int]] = []
    for result in results:
        if not result:
            continue
        if ranges and result[0][0] == ranges[-1][0] + ranges[-1][1]:
            ranges[-1] = (ranges[-1][0], ranges[-1][1] + result[0][1])
            ranges.extend(result[1:])
        else:
            ranges.extend(result)

    return ranges
