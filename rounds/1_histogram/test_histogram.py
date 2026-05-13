"""Round 1 — correctness tests and benchmarks for the byte-pair histogram.

The ``implementation`` fixture below is parametrized over the baseline and your
solution, so every test that takes it runs twice — once per implementation.

Run correctness from the repo root:

    uv run pytest rounds/1_histogram/

Run the benchmark (walltime):

    uv run pytest --codspeed rounds/1_histogram/
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from .baseline import compute_histogram as baseline_impl
from .solution import compute_histogram as solution_impl

DATA_DIR = Path(__file__).parent / "data"
FIXTURE_PATH = DATA_DIR / "fixture_payload.bin"
PAYLOAD_PATH = DATA_DIR / "payload.bin"


@pytest.fixture(
    params=[baseline_impl, solution_impl], ids=["baseline", "solution"]
)
def implementation(request: pytest.FixtureRequest):
    """The function under test — yields baseline, then solution."""
    return request.param


def _reference_histogram(path: Path) -> dict[bytes, int]:
    """Trivially correct reference. Slow, but obviously right."""
    data = path.read_bytes()
    return dict(Counter(bytes(pair) for pair in zip(data, data[1:])))


@pytest.fixture(scope="module")
def fixture_path() -> Path:
    if not FIXTURE_PATH.exists():
        pytest.fail(
            f"missing fixture: {FIXTURE_PATH}\n"
            "Run `python scripts/setup.py` (or `python rounds/1_histogram/gen_data.py`) first."
        )
    return FIXTURE_PATH


def test_matches_reference(implementation, fixture_path: Path) -> None:
    result = implementation(str(fixture_path))
    expected = _reference_histogram(fixture_path)
    assert result == expected


def test_total_count_equals_bigram_count(
    implementation, fixture_path: Path
) -> None:
    result = implementation(str(fixture_path))
    expected_total = fixture_path.stat().st_size - 1
    assert sum(result.values()) == expected_total


def test_bench_compute_histogram(implementation, benchmark) -> None:
    if not PAYLOAD_PATH.exists():
        pytest.skip(
            f"missing payload: {PAYLOAD_PATH}. Run `python scripts/setup.py` first."
        )
    result = benchmark(implementation, str(PAYLOAD_PATH))
    assert sum(result.values()) > 0
