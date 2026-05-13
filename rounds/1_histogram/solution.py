"""Your Round 1 solution — byte-pair histogram.

Strategy: a tiny native extension does the counting, and Python only walks
the 65 536-bucket result once to materialize the ``dict[bytes, int]``.

- ``histogram_native.c`` mmaps the file, hints SEQUENTIAL access to the
  kernel, and delegates the hot loop to a hand-written ARM64 assembly
  routine in ``histogram_native.S`` (one 64-bit ``ldr`` + 8 ``ubfx``
  extracts per chunk replace 8 ``ldrh`` load µops). On non-aarch64 hosts
  the .c file falls back to an equivalent 8x-unrolled C loop.
- The extension is auto-compiled with ``cc -O3`` the first time it is
  imported and cached under ``__pycache__/``. Rebuilds whenever any
  source file outpaces the binary.
- The bin id is the LE-uint16 value of (b0, b1), i.e. ``b1 << 8 | b0``;
  ``_KEY_TABLE`` is precomputed to match so the final dict build is a
  single tight comprehension with no per-bigram byte object allocation.
"""

from __future__ import annotations

import ctypes
import os
import platform
import subprocess
import sys
from pathlib import Path

assert sys.byteorder == "little", (
    "histogram_native.c uses LE-encoded bin ids; port to BE if you need it."
)

_BUCKETS = 65536
_COUNTS_TYPE = ctypes.c_uint64 * _BUCKETS
_KEY_TABLE = tuple(
    bytes((i & 0xFF, (i >> 8) & 0xFF)) for i in range(_BUCKETS)
)
_LIB: ctypes.CDLL | None = None


def compute_histogram(path: str) -> dict[bytes, int]:
    """Frequency of every 2-byte bigram in the file at ``path``."""
    counts = _COUNTS_TYPE()
    rc = _load_library().histogram_count_file(os.fsencode(path), counts)
    if rc != 0:
        raise OSError(rc, os.strerror(rc), path)
    keys = _KEY_TABLE
    return {keys[i]: n for i, n in enumerate(counts) if n}


def _load_library() -> ctypes.CDLL:
    global _LIB
    if _LIB is not None:
        return _LIB

    here = Path(__file__).parent
    c_source = here / "histogram_native.c"
    sources = [c_source]
    if platform.machine() in ("arm64", "aarch64"):
        sources.append(here / "histogram_native.S")

    cache_dir = here / "__pycache__"
    cache_dir.mkdir(exist_ok=True)
    library = cache_dir / "histogram_native.so"

    if not library.exists() or any(
        s.stat().st_mtime > library.stat().st_mtime for s in sources
    ):
        cc = os.environ.get("CC", "cc")
        subprocess.run(
            [
                cc,
                "-O3",
                "-std=c99",
                "-shared",
                "-fPIC",
                *[str(s) for s in sources],
                "-o",
                str(library),
            ],
            check=True,
        )

    lib = ctypes.CDLL(str(library))
    lib.histogram_count_file.argtypes = [
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.c_uint64),
    ]
    lib.histogram_count_file.restype = ctypes.c_int
    _LIB = lib
    return lib
