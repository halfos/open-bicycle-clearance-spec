"""Tyre and fender fit calculations from Level B profiles."""

from .models import MARGINS, FitResult
from .profile import InsufficientCoverage, Polyline
from .reference_shapes import fender_outer_radius, tyre_half_width, tyre_outer_radius


def check_tyre(
    profile: dict,
    bsd: int,
    width: float,
    margin: str = "all-road",
    fender: bool = False,
) -> FitResult:
    if margin not in MARGINS:
        raise ValueError(f"unknown margin class {margin!r}")
    try:
        outer = fender_outer_radius(bsd, width) if fender else tyre_outer_radius(bsd, width)
        start = bsd / 2
        left = Polyline([tuple(point) for point in profile["z_free_left"]])
        right = Polyline([tuple(point) for point in profile["z_free_right"]])
        if not left.covers(start, outer) or not right.covers(start, outer):
            raise InsufficientCoverage("profile does not cover the reference shape")
        radii = sorted(set(left.sample(start, outer) + right.sample(start, outer)))
        binding = None
        min_gap = float("inf")
        for radius in radii:
            half_width = tyre_half_width(bsd, width, radius)
            if fender:
                half_width += 5.0
            for side, line in (("left", left), ("right", right)):
                gap = line.at(radius) - half_width
                if gap < min_gap:
                    min_gap = gap
                    binding = {"r": float(radius), "side": side}
        radial_gap = float(profile["max_radius"]) - outer
        if radial_gap < min_gap:
            min_gap = radial_gap
            binding = {"r": float(outer), "side": "radial"}
        fits = min_gap >= MARGINS[margin]
        return FitResult(
            status="fit" if fits else "no-fit",
            fits=fits,
            gap=round(min_gap, 2),
            binding_point=binding,
            margin_class=margin,
        )
    except (KeyError, TypeError, ValueError):
        return FitResult(status="insufficient data", fits=None, margin_class=margin)


def check_matrix_cell(gap: int | str | dict | None, margin: str = "all-road") -> bool | None:
    if margin not in MARGINS:
        raise ValueError(f"unknown margin class {margin!r}")
    if gap is None:
        return None
    if gap == "x":
        return False
    value = gap.get("gap") if isinstance(gap, dict) else gap
    return None if value is None else float(value) >= MARGINS[margin]
