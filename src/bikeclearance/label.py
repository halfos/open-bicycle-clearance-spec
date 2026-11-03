"""Consumer-facing label generation."""

import html

from .fit import check_matrix_cell

COMMON_NAMES = {
    406: "20-inch",
    559: "26-inch",
    584: "650b / 27.5-inch",
    622: "700c / 28-inch / 29-inch",
    686: "32-inch (BSD to be verified against ETRTO)",
    349: "16-inch",
    451: "20-inch",
    507: "24-inch",
    520: "650c",
    571: "650c",
    590: "650a",
    630: "27-inch",
    635: "700a",
}


def render_label(record: dict, margin: str = "all-road") -> str:
    frame = record["frame"]
    level_a = record["level_a"]
    matrices = level_a["matrices"]
    lines = [
        f"{frame['brand']} / {frame['model']} / {frame['year']} / {frame['size']}",
        f"Margin: {margin} ({ {'road': 4, 'all-road': 6, 'mud': 10}[margin] } mm)",
    ]
    for bsd in sorted(set(matrices["without_fender"]) | set(matrices["with_fender"]), key=int):
        names = []
        for condition, display in (
            ("without_fender", "without fender"),
            ("with_fender", "with fender"),
        ):
            row = matrices[condition].get(str(bsd), {})
            passing = []
            for width, cell in row.items():
                if check_matrix_cell(cell, margin):
                    passing.append(int(width))
            names.append(f"{max(passing)} mm {display}" if passing else f"none {display}")
        common = COMMON_NAMES.get(int(bsd), "common name not specified")
        lines.append(f"{bsd} ({common}): {names[0]}; {names[1]}")

    chainrings = level_a.get("chainrings")
    if chainrings:
        setup = []
        if chainrings.get("two_by_combinations"):
            setup.append(
                "2x "
                + ", ".join(
                    "/".join(map(str, pair)) + "T" for pair in chainrings["two_by_combinations"]
                )
            )
        if chainrings.get("one_by_max_teeth"):
            setup.append(
                "1x max "
                + ", ".join(
                    f"{teeth}T at {chainline} mm"
                    for chainline, teeth in chainrings["one_by_max_teeth"].items()
                )
            )
        if chainrings.get("fd_mount"):
            setup.append(f"front derailleur: {chainrings['fd_mount']}")
        if setup:
            lines.append("Chainrings: " + "; ".join(setup))
    lines.append(
        "Fender mounts: " + (", ".join(level_a.get("fender_mounts", [])) or "none declared")
    )
    conditions = record.get("reference_conditions", {}).get("description", "not specified")
    provenance = record.get("provenance", {}).get("source", "not specified")
    lines.append(f"Conditions: {conditions}; provenance: {provenance}")
    return "\n".join(lines)


def render_label_html(record: dict, margin: str = "all-road") -> str:
    return "<pre>" + html.escape(render_label(record, margin)) + "</pre>"
