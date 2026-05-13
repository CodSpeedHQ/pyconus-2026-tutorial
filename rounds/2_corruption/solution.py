"""Your Round 2 solution - corruption scanner."""

from __future__ import annotations

import mmap


_BLOCK_SIZE = 4096


def find_corruptions(ref_path: str, cor_path: str) -> list[tuple[int, int]]:
    """ Return ``[(offset, length), ...]`` for every differing byte range. """

    with open(ref_path, "rb") as ref_file, open(cor_path, "rb") as cor_file:
        # Use the file size as the single source of truth before mapping.
        size = ref_file.seek(0, 2)
        if size != cor_file.seek(0, 2):
            raise ValueError("reference and corrupted files differ in length")
        if size == 0:
            return []

        ref_file.seek(0)
        cor_file.seek(0)

        with mmap.mmap(ref_file.fileno(), 0, access=mmap.ACCESS_READ) as ref:
            with mmap.mmap(cor_file.fileno(), 0, access=mmap.ACCESS_READ) as cor:
                ranges: list[tuple[int, int]] = []
                # -1 means there is no currently open corruption range.
                run_start = -1
                append = ranges.append
                block_size = _BLOCK_SIZE

                for block_start in range(0, size, block_size):
                    block_end = min(block_start + block_size, size)

                    # Most blocks are identical, so skip them with a C-level
                    # bytes comparison instead of a Python loop over each byte.
                    if ref[block_start:block_end] == cor[block_start:block_end]:
                        if run_start != -1:
                            append((run_start, block_start - run_start))
                            run_start = -1
                        continue

                    # Only scan inside blocks that actually differ. Keeping
                    # run_start outside this loop lets ranges cross block edges.
                    for pos in range(block_start, block_end):
                        if ref[pos] != cor[pos]:
                            if run_start == -1:
                                run_start = pos
                        elif run_start != -1:
                            append((run_start, pos - run_start))
                            run_start = -1

                # Close a corruption range that reaches the end of the file.
                if run_start != -1:
                    append((run_start, size - run_start))

                return ranges
