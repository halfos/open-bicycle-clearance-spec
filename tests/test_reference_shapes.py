import pytest

from bikeclearance.reference_shapes import (
    approximate_outer_diameter,
    chainring_pitch_diameter,
    tyre_half_width,
    tyre_outer_radius,
)


def test_reference_tyre_geometry():
    assert tyre_outer_radius(622, 50) == pytest.approx(358.5)
    assert tyre_half_width(622, 50, 311 + 0.45 * 50) == pytest.approx(25)
    assert tyre_half_width(622, 50, 311) == pytest.approx(50 * (0.25 - 0.45**2) ** 0.5)
    assert approximate_outer_diameter(622, 50) == pytest.approx(717)


@pytest.mark.parametrize(
    ("teeth", "diameter"),
    [(34, 137.6), (40, 161.9), (46, 186.1), (50, 202.3), (53, 214.4)],
)
def test_chainring_pitch_diameter_table(teeth, diameter):
    assert chainring_pitch_diameter(teeth) == pytest.approx(diameter, abs=0.05)
