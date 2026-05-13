"""Your Round 1 solution — byte-pair histogram.

Strategy: count every 2-byte bigram in C-loop time with ``numpy.bincount``.

1. Read the payload as raw bytes and wrap it in a zero-copy ``uint8`` view.
2. Reinterpret the buffer as ``uint16`` at two offsets (even bytes, odd bytes)
   — together these two non-overlapping strides cover every overlapping
   bigram in the file. Two ``np.bincount`` calls on the views, summed, give
   the count of every possible 2-byte token.
3. Walk the dense 65,536-bin array once in Python and emit a ``dict`` for the
   nonzero entries, looking up pre-built ``bytes`` keys from a module-level
   table so we never allocate two-byte ``bytes`` objects on the hot path.

This relies on the host being little-endian (every modern x86/ARM target is);
on a big-endian platform the fallback shift-and-or path is used. The bigram
arrays are never materialized, so peak memory is the file size plus a 64 KiB
counts buffer.
"""

from __future__ import annotations

import sys

import numpy as np

_LITTLE_ENDIAN = sys.byteorder == "little"

# Bigram id -> 2-byte key. The id encoding depends on which path we take.
# Little-endian uint16 view of bytes (b0, b1) has value b1<<8 | b0, so the key
# at index i is bytes((i & 0xFF, i >> 8)). The big-endian fallback uses the
# more natural id (b0<<8 | b1), so the key at index i is bytes((i >> 8, i & 0xFF)).
if _LITTLE_ENDIAN:
    _KEY_TABLE: tuple[bytes, ...] = tuple(
        bytes((i & 0xFF, i >> 8)) for i in range(65536)
    )
else:  # pragma: no cover — exercised only on big-endian hosts
    _KEY_TABLE = tuple(bytes((i >> 8, i & 0xFF)) for i in range(65536))


def _bincount_le(arr: np.ndarray) -> np.ndarray:
    """Two-pass uint16 view, no bigram-id materialization."""
    n = arr.size
    even = arr[: n - (n % 2)].view(np.uint16)
    odd_len = (n - 1) - ((n - 1) % 2)
    odd = arr[1 : 1 + odd_len].view(np.uint16)
    return np.bincount(even, minlength=65536) + np.bincount(
        odd, minlength=65536
    )


def _bincount_be(arr: np.ndarray) -> np.ndarray:
    """Portable shift-and-or path for big-endian hosts."""
    bigrams = (arr[:-1].astype(np.uint16) << 8) | arr[1:]
    return np.bincount(bigrams, minlength=65536)


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    with open(path, "rb") as f:
        data = f.read()
    arr = np.frombuffer(data, dtype=np.uint8)
    if arr.size < 2:
        return {}
    counts = _bincount_le(arr) if _LITTLE_ENDIAN else _bincount_be(arr)
    keys = _KEY_TABLE
    out: dict[bytes, int] = {}
    for i, n in enumerate(counts.tolist()):
        if n:
            out[keys[i]] = n
    return out
