from __future__ import annotations

import json
from pathlib import Path
import sys

root_dir = Path(__file__).resolve().parents[1]
sys.path.append(str(root_dir))

from genetic_health_coach.cli import main


def _sample_vcf_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sample_data" / "example_annotated.vcf"


def test_cli_outputs_text(capsys) -> None:
    exit_code = main([str(_sample_vcf_path())])
    assert exit_code == 0
    captured = capsys.readouterr().out
    assert "Subiect: Nutriție" in captured
    assert "- Recomandări:" in captured


def test_cli_supports_json(capsys) -> None:
    exit_code = main([str(_sample_vcf_path()), "--json", "--subject", "sport"])
    assert exit_code == 0
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["requested_subjects"] == ["sport"]
    assert payload["subjects"][0]["subject"] == "sport"


def test_cli_can_write_to_file(tmp_path: Path, capsys) -> None:
    destination = tmp_path / "out" / "raport.txt"
    exit_code = main([str(_sample_vcf_path()), "--subject", "terapii", "--output", str(destination)])
    assert exit_code == 0
    assert destination.exists()
    content = destination.read_text(encoding="utf-8")
    assert "Subiect: Terapii" in content
    # Stdout should remain empty when writing to file.
    assert capsys.readouterr().out == ""
