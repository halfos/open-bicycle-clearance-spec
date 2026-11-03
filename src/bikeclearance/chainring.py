"""Chainring envelope checks."""

from .models import ChainringResult
from .profile import InsufficientCoverage, Polyline
from .reference_shapes import chainring_envelope_radius, chainring_pitch_diameter


def check_chainring(
    profile: list, teeth: int, chainline: float, margin: float = 3.0
) -> ChainringResult:
    pitch = chainring_pitch_diameter(teeth)
    radius = chainring_envelope_radius(teeth)
    required = radius + margin
    try:
        line = Polyline([tuple(point) for point in profile])
        start = line.coverage[0]
        if not line.covers(start, required):
            raise InsufficientCoverage
        samples = line.sample(start, required)
        limit = chainline - 3.0 - margin
        binding = max(samples, key=lambda radial: line.at(radial))
        fits = all(line.at(radial) <= limit for radial in samples)
        return ChainringResult(
            fits=fits,
            status="fit" if fits else "no-fit",
            pitch_diameter=round(pitch, 1),
            envelope_radius=round(radius, 2),
            binding_radius=float(binding) if not fits else None,
        )
    except (TypeError, ValueError):
        return ChainringResult(
            fits=None,
            status="insufficient data",
            pitch_diameter=round(pitch, 1),
            envelope_radius=round(radius, 2),
        )
