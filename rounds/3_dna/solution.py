"""Your Round 3 solution — DNA sequence matcher.

**Edit this file.** It currently delegates to ``baseline.py`` so everything
passes out of the box. Replace the body of ``find_matches`` with your
own faster implementation.
"""

from mmap import mmap, ACCESS_READ
from concurrent.futures import ThreadPoolExecutor, wait

def _subsearch(raw, record_id_start: int, data_start: int, data_end: int, pattern: bytes):
    plen = len(pattern)
    data = bytes(raw[data_start : data_end - 1]).replace(b"\n", b"")
    locations = []
    loc = data.find(pattern)
    while loc != -1:
        locations.append(loc)
        loc = data.find(pattern, loc + plen)

    if not locations:
        return None

    record_id = raw[record_id_start : data_start - 1].decode("ascii")
    return (record_id, locations)

def find_matches(fasta_path: str, pattern: bytes) -> list[tuple[str, list[int]]]:
    """Find every FASTA record whose sequence contains ``pattern``.

    Returns ``[(record_id, [positions...]), ...]`` in file order.
    """
    source = open(fasta_path, "rb")
    data = mmap(source.fileno(), 0, access=ACCESS_READ)

    last = -1

    data_end = len(data) - 1
    while data[data_end] == b"\n":
        data_end -= 1

    with ThreadPoolExecutor(max_workers=16) as executor:
        records = []
        while data_end > 0:
            gt_pos = data.rfind(b">", 0, data_end)
            if gt_pos == -1:
                raise Exception("expected greater than")

            record_id_start = gt_pos + 1

            nl_pos = data.find(b"\n", record_id_start)
            if nl_pos == -1:
                raise Exception("expected new line")

            data_start = nl_pos + 1

            records.append(
                executor.submit(_subsearch, data, record_id_start, data_start, data_end, pattern)
            )
            data_end = gt_pos

        results = [d.result() for d in records if d.result() is not None]
        results.reverse()
        return results
