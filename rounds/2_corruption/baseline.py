from __future__ import annotations

import mmap
import os
from os import PathLike
from typing import Union

import numpy as np


Pathish = Union[str, bytes, PathLike[str], PathLike[bytes]]


def find_corruptions(
    ref_path: Pathish,
    cor_path: Pathish,
    *,
    chunk_size: int = 1 << 26,  # 64 MiB
) -> list[tuple[int, int]]:
    """
    Return [(offset, length), ...] for every differing byte range.

    Optimizations:
    - checks file sizes before reading
    - memory-maps both files
    - compares bytes using NumPy's native vectorized code
    - records only transition points, not every differing offset
    - handles corruption ranges that cross chunk boundaries
    """

    ref_size = os.path.getsize(ref_path)
    cor_size = os.path.getsize(cor_path)

    if ref_size != cor_size:
        raise ValueError("reference and corrupted files differ in length")

    if ref_size == 0:
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    chunk_size = min(chunk_size, ref_size)

    ranges: list[tuple[int, int]] = []
    append = ranges.append

    in_run = False
    run_start = 0

    # Reuse this buffer so we do not allocate a new boolean array per chunk.
    diff_buffer = np.empty(chunk_size, dtype=np.bool_)

    with open(ref_path, "rb") as ref_file, open(cor_path, "rb") as cor_file:
        with (
            mmap.mmap(ref_file.fileno(), 0, access=mmap.ACCESS_READ) as ref_map,
            mmap.mmap(cor_file.fileno(), 0, access=mmap.ACCESS_READ) as cor_map,
        ):
            for offset in range(0, ref_size, chunk_size):
                stop = min(offset + chunk_size, ref_size)
                length = stop - offset

                ref_chunk = np.frombuffer(
                    ref_map,
                    dtype=np.uint8,
                    count=length,
                    offset=offset,
                )
                cor_chunk = np.frombuffer(
                    cor_map,
                    dtype=np.uint8,
                    count=length,
                    offset=offset,
                )

                diff = diff_buffer[:length]
                np.not_equal(ref_chunk, cor_chunk, out=diff)

                # Fast path: this entire chunk is identical.
                if not bool(diff.any()):
                    if in_run:
                        append((run_start, offset - run_start))
                        in_run = False

                    del ref_chunk, cor_chunk, diff
                    continue

                # Fast path: this entire chunk differs.
                if bool(diff.all()):
                    if not in_run:
                        run_start = offset
                        in_run = True

                    del ref_chunk, cor_chunk, diff
                    continue

                # Handle a transition at the chunk boundary.
                first_is_diff = bool(diff[0])
                if first_is_diff != in_run:
                    if in_run:
                        append((run_start, offset - run_start))
                        in_run = False
                    else:
                        run_start = offset
                        in_run = True

                # Internal transitions:
                # False -> True starts a corruption range.
                # True -> False closes a corruption range.
                transitions = np.flatnonzero(diff[1:] != diff[:-1]) + 1

                for transition in transitions:
                    pos = offset + int(transition)

                    if in_run:
                        append((run_start, pos - run_start))
                        in_run = False
                    else:
                        run_start = pos
                        in_run = True

                # Release mmap-backed NumPy views before closing mmap objects.
                del ref_chunk, cor_chunk, diff, transitions

            if in_run:
                append((run_start, ref_size - run_start))

    return ranges
