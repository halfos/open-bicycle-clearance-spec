"""Command-line interface for OBCS."""

import csv
import json
import tempfile
from pathlib import Path

import typer
import yaml
from jsonschema import Draft202012Validator

from .chainring import check_chainring as evaluate_chainring
from .fit import check_tyre as evaluate_tyre
from .label import render_label, render_label_html
from .matrix import consistency as compare_matrix
from .matrix import neighbouring_bsds, predict_matrix
from .models import CORE_BSDS, CORE_WIDTHS
from .plot import plot_record
from .profile import Polyline

app = typer.Typer(no_args_is_help=True, help="Validate and inspect OBCS bicycle clearance data.")
SCHEMA_PATH = Path(__file__).with_name("obcs.schema.json")
if not SCHEMA_PATH.is_file():
    SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema" / "obcs.schema.json"


def load_record(path: Path) -> dict:
    with path.open(encoding="utf-8") as source:
        value = yaml.safe_load(source)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: document must contain a mapping")

    def string_keys(item):
        if isinstance(item, dict):
            return {str(key): string_keys(child) for key, child in item.items()}
        if isinstance(item, list):
            return [string_keys(child) for child in item]
        return item

    return string_keys(value)


def validate_record(path: Path) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    record = load_record(path)
    Draft202012Validator(schema).validate(record)
    for profile in record.get("level_b", {}).get("profiles", {}).values():
        for side in ("z_free_left", "z_free_right", "bb_profile_drive"):
            if side in profile:
                Polyline([tuple(point) for point in profile[side]])


@app.command()
def validate(files: list[Path] = typer.Argument(..., exists=True, readable=True)):
    """Validate one or more OBCS YAML records."""
    for path in files:
        try:
            validate_record(path)
        except Exception as error:
            typer.echo(f"{path}: invalid: {error}", err=True)
            raise typer.Exit(1) from error
        typer.echo(f"{path}: valid")


@app.command("check-tyre")
def check_tyre(
    file: Path = typer.Argument(..., exists=True),
    bsd: int = typer.Option(..., min=1, help="Exact bead-seat diameter in mm."),
    width: float = typer.Option(..., min=1, help="Measured tyre width in mm."),
    margin: str = typer.Option("all-road"),
    fender: bool = typer.Option(False, help="Check the reference fender envelope."),
):
    """Check a tyre against a Level B profile."""
    record = load_record(file)
    profile = record.get("level_b", {}).get("profiles", {}).get(str(bsd))
    result = evaluate_tyre(profile or {}, bsd, width, margin, fender)
    typer.echo(result.model_dump_json())


@app.command("check-chainring")
def check_chainring(
    file: Path = typer.Argument(..., exists=True),
    teeth: int = typer.Option(..., min=1),
    chainline: float = typer.Option(..., min=1),
):
    """Check a chainring against the drive-side BB profile."""
    record = load_record(file)
    profiles = record.get("level_b", {}).get("profiles", {})
    drive = next(
        (
            profile.get("bb_profile_drive")
            for profile in profiles.values()
            if profile.get("bb_profile_drive")
        ),
        [],
    )
    result = evaluate_chainring(drive, teeth, chainline)
    typer.echo(result.model_dump_json())


@app.command("predict-matrix")
def predict_matrix_command(file: Path = typer.Argument(..., exists=True)):
    """Predict Level A gaps from Level B profiles."""
    typer.echo(json.dumps(predict_matrix(load_record(file)), indent=2))


@app.command("consistency")
def consistency_command(file: Path = typer.Argument(..., exists=True)):
    """Report Level A/Level B differences greater than 2 mm."""
    typer.echo(json.dumps(compare_matrix(load_record(file)), indent=2))


@app.command("label")
def label_command(
    file: Path = typer.Argument(..., exists=True),
    output_format: str = typer.Option("md", "--format", help="Output format: md or html."),
    margin: str = typer.Option("all-road"),
):
    """Generate a consumer-facing label."""
    record = load_record(file)
    if output_format not in {"md", "html"}:
        raise typer.BadParameter("format must be md or html")
    output = (
        render_label_html(record, margin)
        if output_format == "html"
        else render_label(record, margin)
    )
    typer.echo(output)


@app.command("plot")
def plot_command(
    file: Path = typer.Argument(..., exists=True),
    output: Path = typer.Option(..., "-o", "--output"),
):
    """Plot a Level B profile and reference tyre."""
    plot_record(load_record(file), str(output))
    typer.echo(str(output))


@app.command("matrix-sheet")
def matrix_sheet(
    bsd: int = typer.Option(..., help="Nominal BSD in mm."),
    output: Path = typer.Option(..., "-o", "--output"),
):
    """Create a printable blank Level A matrix and fender checklist."""
    bsds = sorted(set(CORE_BSDS + neighbouring_bsds(bsd)))
    widths = CORE_WIDTHS
    header = "".join(f"<th>{width}</th>" for width in widths)
    rows = "".join(
        f"<tr><th>{size} mm</th><td>" + "</td><td>".join("" for _ in widths) + "</td></tr>"
        for size in bsds
    )
    html = (
        "<!doctype html><meta charset='utf-8'><title>OBCS matrix sheet</title>"
        f"<h1>OBCS blank matrix — BSD {bsd} mm (neighbouring sizes included)</h1>"
        "<p>Record the smallest gap in mm, x for no fit, blank for untested.</p>"
        f"<table border='1'><thead><tr><th>BSD</th>{header}</tr></thead>"
        f"<tbody>{rows}</tbody></table>"
        "<h2>Fender mounts</h2><p>"
        + " ".join(
            f"&#9744; {mount}"
            for mount in (
                "dropout_f",
                "dropout_r",
                "crown_hole",
                "mid_fork",
                "ss_bridge",
                "cs_bridge",
                "other",
            )
        )
        + "</p>"
    )
    output.write_text(html, encoding="utf-8")
    typer.echo(str(output))


@app.command("export-csv")
def export_csv(
    file: Path = typer.Argument(..., exists=True),
    output: Path = typer.Option(..., "-o", "--output"),
):
    """Export Level A matrix cells to CSV."""
    record = load_record(file)
    with output.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=["condition", "bsd", "width", "gap"])
        writer.writeheader()
        for condition, matrix in record["level_a"]["matrices"].items():
            for bsd, widths in matrix.items():
                for width, cell in widths.items():
                    gap = cell.get("gap") if isinstance(cell, dict) else cell
                    writer.writerow(
                        {"condition": condition, "bsd": bsd, "width": width, "gap": gap}
                    )
    typer.echo(str(output))


@app.command("import-csv")
def import_csv(
    file: Path = typer.Argument(..., exists=True),
    csv_file: Path = typer.Argument(..., exists=True),
    output: Path = typer.Option(..., "-o", "--output"),
):
    """Import Level A cells from CSV into a record YAML."""
    record = load_record(file)
    for condition in ("without_fender", "with_fender"):
        record["level_a"]["matrices"][condition] = {}
    with csv_file.open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            condition, bsd, width, value = row["condition"], row["bsd"], row["width"], row["gap"]
            if condition not in record["level_a"]["matrices"]:
                raise ValueError(f"unknown matrix condition: {condition}")
            cell = None if value == "" else ("x" if value == "x" else int(value))
            record["level_a"]["matrices"][condition].setdefault(bsd, {})[width] = cell
    output.write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")
    typer.echo(str(output))


@app.command("check-generated")
def check_generated():
    """Verify committed example labels and figures match generated output."""
    examples = Path(__file__).resolve().parents[2] / "examples"
    for path in sorted(examples.glob("*.yaml")):
        record = load_record(path)
        expected_label = path.with_suffix(".md").read_text(encoding="utf-8")
        if render_label(record) + "\n" != expected_label:
            raise typer.BadParameter(f"stale generated label: {path.with_suffix('.md')}")
        with tempfile.TemporaryDirectory() as directory:
            generated = Path(directory) / "figure.svg"
            plot_record(record, str(generated))
            committed = path.with_suffix(".svg").read_text(encoding="utf-8")
            if generated.read_text(encoding="utf-8") != committed:
                raise typer.BadParameter(f"stale generated figure: {path.with_suffix('.svg')}")
    typer.echo("Generated labels and figures are up to date.")


if __name__ == "__main__":
    app()
