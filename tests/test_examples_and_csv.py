from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from bikeclearance.cli import app, load_record, validate_record
from bikeclearance.label import render_label

ROOT = Path(__file__).resolve().parents[1]
RUNNER = CliRunner()


def test_all_examples_validate_and_labels_are_current():
    examples = sorted((ROOT / "examples").glob("*.yaml"))
    assert len(examples) == 4
    for path in examples:
        validate_record(path)
        assert (
            path.with_suffix(".md").read_text(encoding="utf-8")
            == render_label(load_record(path)) + "\n"
        )
        assert path.with_suffix(".svg").is_file()


def test_csv_round_trip(tmp_path):
    source = ROOT / "examples" / "gravel.yaml"
    csv_path = tmp_path / "matrix.csv"
    output = tmp_path / "roundtrip.yaml"
    exported = RUNNER.invoke(app, ["export-csv", str(source), "-o", str(csv_path)])
    assert exported.exit_code == 0, exported.output
    imported = RUNNER.invoke(app, ["import-csv", str(source), str(csv_path), "-o", str(output)])
    assert imported.exit_code == 0, imported.output
    original = load_record(source)["level_a"]["matrices"]
    returned = load_record(output)["level_a"]["matrices"]
    assert returned == original
    assert yaml.safe_load(output.read_text(encoding="utf-8"))["level_a"]["matrices"] == original


def test_matrix_sheet_includes_core_and_neighboring_sizes(tmp_path):
    output = tmp_path / "sheet.html"
    result = RUNNER.invoke(app, ["matrix-sheet", "--bsd", "622", "-o", str(output)])
    assert result.exit_code == 0, result.output
    html = output.read_text(encoding="utf-8")
    for bsd in (406, 559, 584, 597, 622, 630, 686):
        assert f"{bsd} mm" in html


def test_validation_rejects_unsorted_profile_radii(tmp_path):
    record = load_record(ROOT / "examples" / "gravel.yaml")
    record["level_b"]["profiles"]["622"]["z_free_left"].reverse()
    path = tmp_path / "unsorted.yaml"
    path.write_text(yaml.safe_dump(record), encoding="utf-8")
    with pytest.raises(ValueError, match="strictly increasing"):
        validate_record(path)
