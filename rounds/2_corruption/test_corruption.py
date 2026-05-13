"""Round 2 — correctness tests and benchmarks for the corruption scanner.

The ``implementation`` fixture below is parametrized over the baseline and your
solution, so every test that takes it runs twice — once per implementation.

Run correctness from the repo root:

    uv run pytest rounds/2_corruption/

Run the benchmark (walltime):

    uv run pytest --codspeed rounds/2_corruption/
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .baseline import find_corruptions as baseline_impl
from .solution import find_corruptions as solution_impl

DATA_DIR = Path(__file__).parent / "data"
REF_PATH = DATA_DIR / "reference.bin"
COR_PATH = DATA_DIR / "corrupted.bin"


@pytest.fixture(
    params=[baseline_impl, solution_impl], ids=["baseline", "solution"]
)
def implementation(request: pytest.FixtureRequest):
    """The function under test — yields baseline, then solution."""
    return request.param


@pytest.fixture(scope="module")
def fixture_paths() -> tuple[Path, Path, list[tuple[int, int]]]:
    ref = DATA_DIR / "fixture_reference.bin"
    cor = DATA_DIR / "fixture_corrupted.bin"
    truth_file = DATA_DIR / "fixture_truth.json"
    if not (ref.exists() and cor.exists() and truth_file.exists()):
        pytest.fail(
            f"missing fixture under {DATA_DIR}\n"
            "Run `python scripts/setup.py` (or `python rounds/2_corruption/gen_data.py`) first."
        )
    truth = json.loads(truth_file.read_text())
    expected = [tuple(r) for r in truth["ranges"]]
    return ref, cor, expected


def test_matches_truth(
    implementation,
    fixture_paths: tuple[Path, Path, list[tuple[int, int]]],
) -> None:
    ref, cor, expected = fixture_paths
    result = implementation(str(ref), str(cor))
    assert result == expected


def test_identical_files_yield_no_ranges(implementation, tmp_path: Path) -> None:
    a = tmp_path / "a.bin"
    a.write_bytes(b"hello world" * 1000)
    b = tmp_path / "b.bin"
    b.write_bytes(a.read_bytes())
    assert implementation(str(a), str(b)) == []


def test_bench_find_corruptions(implementation, benchmark) -> None:
    if not (REF_PATH.exists() and COR_PATH.exists()):
        pytest.skip(
            f"missing dataset under {DATA_DIR}. Run `python scripts/setup.py` first."
        )
    result = benchmark(implementation, str(REF_PATH), str(COR_PATH))
    assert isinstance(result, list)
