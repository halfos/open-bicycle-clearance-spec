"""Level A matrix prediction, consistency, and BSD-neighbour helpers."""

from .fit import check_tyre
from .models import CORE_BSDS, CORE_WIDTHS, EXTENDED_BSDS


def neighbouring_bsds(bsd: int) -> list[int]:
    sizes = sorted(set(CORE_BSDS + EXTENDED_BSDS))
    if bsd not in sizes:
        sizes.append(bsd)
        sizes.sort()
    index = sizes.index(bsd)
    return sizes[max(0, index - 1) : min(len(sizes), index + 2)]


def predict_matrix(record: dict, widths: list[int] | None = None, margin: str = "all-road") -> dict:
    widths = widths or CORE_WIDTHS
    predicted = {"without_fender": {}, "with_fender": {}}
    profiles = record.get("level_b", {}).get("profiles", {})
    for bsd, profile in profiles.items():
        for condition, use_fender in (("without_fender", False), ("with_fender", True)):
            predicted[condition][str(bsd)] = {}
            for width in widths:
                result = check_tyre(profile, int(bsd), width, margin, use_fender)
                predicted[condition][str(bsd)][str(width)] = (
                    round(result.gap) if result.status != "insufficient data" else None
                )
    return predicted


def consistency(record: dict, tolerance: float = 2.0) -> list[dict]:
    predictions = predict_matrix(record)
    matrices = record.get("level_a", {}).get("matrices", {})
    differences = []
    for condition in ("without_fender", "with_fender"):
        actual_matrix = matrices.get(condition, {})
        for bsd, widths in actual_matrix.items():
            for width, cell in widths.items():
                actual = cell.get("gap") if isinstance(cell, dict) else cell
                predicted = predictions[condition].get(str(bsd), {}).get(str(width))
                if isinstance(actual, int) and isinstance(predicted, int):
                    delta = abs(actual - predicted)
                    if delta > tolerance:
                        differences.append(
                            {
                                "condition": condition,
                                "bsd": int(bsd),
                                "width": int(width),
                                "measured": actual,
                                "predicted": predicted,
                                "difference": delta,
                            }
                        )
    return differences
