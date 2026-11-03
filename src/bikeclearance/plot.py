"""SVG profile plotting."""

import json

import matplotlib.pyplot as plt

from .matrix import predict_matrix
from .reference_shapes import tyre_half_width, tyre_outer_radius


def plot_record(record: dict, output: str) -> None:
    with plt.rc_context({"svg.hashsalt": "obcs-v0.1.0"}):
        _plot_record(record, output)


def _plot_record(record: dict, output: str) -> None:
    profiles = record.get("level_b", {}).get("profiles", {})
    if not profiles:
        raise ValueError("record contains no Level B profiles")
    bsd = sorted(profiles, key=int)[0]
    profile = profiles[bsd]
    fig, axis = plt.subplots(figsize=(6, 8))
    axis.plot(
        [point[1] for point in profile["z_free_left"]],
        [point[0] for point in profile["z_free_left"]],
        color="green",
    )
    axis.plot(
        [-point[1] for point in profile["z_free_right"]],
        [point[0] for point in profile["z_free_right"]],
        color="green",
    )
    matrices = predict_matrix(record)
    for condition, color in (("without_fender", "steelblue"), ("with_fender", "darkorange")):
        widths = [
            int(width)
            for width, gap in matrices[condition].get(str(bsd), {}).items()
            if gap is not None and gap >= 6
        ]
        if widths:
            width = max(widths)
            outer = tyre_outer_radius(int(bsd), width)
            if condition == "with_fender":
                outer += 14
            radii = [int(bsd) / 2 + i * (outer - int(bsd) / 2) / 100 for i in range(101)]
            halves = [tyre_half_width(int(bsd), width, radius) for radius in radii]
            if condition == "with_fender":
                halves = [half + 5 for half in halves]
            axis.fill_betweenx(radii, [-half for half in halves], halves, color=color, alpha=0.2)
    axis.set_xlabel("z lateral (mm)")
    axis.set_ylabel("r radial (mm)")
    axis.set_title(f"Clearance profile — BSD {bsd} mm")
    axis.set_aspect("equal", adjustable="datalim")
    axis.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(output, format="svg", metadata={"Date": None, "Description": json.dumps(profile)})
    plt.close(fig)
