"""Unit tests for the genetic health coach tools."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))

from genetic_health_coach.tools.subject_analysis import build_subject_report
from genetic_health_coach.tools.vcf_parser import extract_gene_variants


@pytest.fixture(scope="module")
def sample_vcf_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data" / "example_annotated.vcf"


def test_extract_gene_variants(sample_vcf_path: Path) -> None:
    result = extract_gene_variants(str(sample_vcf_path))
    genes = {entry["gene"] for entry in result["genes"]}

    assert "MTHFR" in genes
    assert "ACTN3" in genes
    assert result["total_variants"] == sum(entry["variant_count"] for entry in result["genes"])
    mthfr_entry = next(entry for entry in result["genes"] if entry["gene"] == "MTHFR")
    assert mthfr_entry["variant_count"] == 1
    variant = mthfr_entry["variants"][0]
    assert variant["impact"] == "MODERATE"
    hgvs_values = [ann.get("hgvs_p") or ann.get("hgvs_c") for ann in variant.get("annotations", [])]
    assert any(value and "p.Ala222Val" in value for value in hgvs_values)


@pytest.mark.parametrize(
    "subject,expected_gene",
    [
        ("nutriție", "MTHFR"),
        ("sport", "ACTN3"),
        ("terapii", "COMT"),
    ],
)
def test_build_subject_report(subject: str, expected_gene: str, sample_vcf_path: Path) -> None:
    gene_data = extract_gene_variants(str(sample_vcf_path))["genes"]
    report = build_subject_report(subject, gene_data)

    assert report["subject"] == subject
    assert any(entry["gene"] == expected_gene for entry in report["entries"])
    assert report["recommendations"], "Recomandările nu ar trebui să fie goale pentru genele cunoscute."
