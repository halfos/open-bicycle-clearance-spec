"""Normative OBCS reference geometry."""

import math


def tyre_outer_radius(bsd: float, width: float) -> float:
    return bsd / 2 + 0.95 * width


def tyre_centre_radius(bsd: float, width: float) -> float:
    return bsd / 2 + 0.45 * width


def tyre_half_width(bsd: float, width: float, radius: float) -> float:
    lower = bsd / 2
    upper = tyre_outer_radius(bsd, width)
    if radius < lower or radius > upper:
        return 0.0
    radicand = (width / 2) ** 2 - (radius - tyre_centre_radius(bsd, width)) ** 2
    return math.sqrt(max(0.0, radicand))


def fender_outer_radius(bsd: float, width: float) -> float:
    return tyre_outer_radius(bsd, width) + 14.0


def chainring_pitch_diameter(teeth: int) -> float:
    if teeth <= 0:
        raise ValueError("teeth must be positive")
    return 12.7 / math.sin(math.pi / teeth)


def chainring_envelope_radius(teeth: int) -> float:
    return chainring_pitch_diameter(teeth) / 2 + 4.0


def approximate_outer_diameter(bsd: float, width: float) -> float:
    return bsd + 2 * 0.95 * width
