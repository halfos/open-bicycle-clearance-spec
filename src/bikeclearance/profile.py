"""Clearance profile interpolation and coverage checks."""

from dataclasses import dataclass

import numpy as np


class InsufficientCoverage(ValueError):
    """Raised when profile data do not span the radii being evaluated."""


@dataclass(frozen=True)
class Polyline:
    points: list[tuple[float, float]]

    def __post_init__(self):
        if len(self.points) < 2:
            raise ValueError("a profile polyline requires at least two points")
        radii = [point[0] for point in self.points]
        if radii != sorted(radii) or len(set(radii)) != len(radii):
            raise ValueError("profile radii must be strictly increasing")
        if any(radius < 0 or value < 0 for radius, value in self.points):
            raise ValueError("profile radii and lateral distances must be non-negative")

    @property
    def coverage(self) -> tuple[float, float]:
        return self.points[0][0], self.points[-1][0]

    def covers(self, lower: float, upper: float) -> bool:
        start, end = self.coverage
        return start <= lower and end >= upper

    def at(self, radius: float) -> float:
        if not self.covers(radius, radius):
            raise InsufficientCoverage(f"profile does not cover radius {radius:g} mm")
        return float(
            np.interp(
                radius, [point[0] for point in self.points], [point[1] for point in self.points]
            )
        )

    def sample(self, lower: float, upper: float, step: float = 1.0) -> list[float]:
        if not self.covers(lower, upper):
            raise InsufficientCoverage(f"profile does not cover {lower:g}–{upper:g} mm")
        radii = {lower, upper}
        radii.update(radius for radius, _ in self.points if lower <= radius <= upper)
        radii.update(np.arange(lower, upper, step).tolist())
        return sorted(radii)
