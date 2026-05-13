"""Round 3 — correctness tests and benchmarks for the DNA sequence matcher.

The ``implementation`` fixture below is parametrized over the baseline and your
solution, so every test that takes it runs twice — once per implementation.

Run correctness from the repo root:

    uv run pytest rounds/3_dna/

Run the benchmark (walltime):

    uv run pytest --codspeed rounds/3_dna/
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .baseline import find_matches as baseline_impl
from .solution import find_matches as solution_impl

DATA_DIR = Path(__file__).parent / "data"
FASTA_PATH = DATA_DIR / "genome.fasta"
TRUTH_PATH = DATA_DIR / "truth.json"


@pytest.fixture(
    params=[baseline_impl, solution_impl], ids=["baseline", "solution"]
)
def implementation(request: pytest.FixtureRequest):
    """The function under test — yields baseline, then solution."""
    return request.param


@pytest.fixture(scope="module")
def fixture() -> tuple[Path, bytes, list[tuple[str, list[int]]]]:
    fasta = DATA_DIR / "fixture_genome.fasta"
    truth_file = DATA_DIR / "fixture_truth.json"
    if not (fasta.exists() and truth_file.exists()):
        pytest.fail(
            f"missing fixture under {DATA_DIR}\n"
            "Run `uv run scripts/setup.py` (or `uv run rounds/3_dna/gen_data.py`) first."
        )
    truth = json.loads(truth_file.read_text())
    pattern = truth["pattern"].encode("ascii")
    expected = [(rid, list(positions)) for rid, positions in truth["matches"]]
    return fasta, pattern, expected


def test_matches_truth(
    implementation,
    fixture: tuple[Path, bytes, list[tuple[str, list[int]]]],
) -> None:
    fasta, pattern, expected = fixture
    result = implementation(str(fasta), pattern)
    assert result == expected


def test_short_synthetic_input(implementation, tmp_path: Path) -> None:
    fasta = tmp_path / "tiny.fasta"
    fasta.write_text(">a\nACGTACGT\n>b\nAGTCCGTAAAA\n")
    result = implementation(str(fasta), b"AGTCCGTA")
    assert result == [("b", [0])]


def test_bench_find_matches(implementation, benchmark) -> None:
    if not FASTA_PATH.exists() or not TRUTH_PATH.exists():
        pytest.skip(
            f"missing dataset under {DATA_DIR}. Run `uv run scripts/setup.py` first."
        )
    pattern = json.loads(TRUTH_PATH.read_text())["pattern"].encode("ascii")
    result = benchmark(implementation, str(FASTA_PATH), pattern)
    assert isinstance(result, list)
