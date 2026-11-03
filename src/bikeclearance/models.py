"""Shared result models and OBCS constants."""

from typing import Literal

from pydantic import BaseModel

MARGINS = {"road": 4.0, "all-road": 6.0, "mud": 10.0}
CORE_BSDS = [406, 559, 584, 622, 686]
EXTENDED_BSDS = [203, 254, 305, 349, 355, 451, 507, 520, 540, 571, 590, 597, 630, 635, 787]
CORE_WIDTHS = list(range(20, 76, 5))


class FitResult(BaseModel):
    status: Literal["fit", "no-fit", "insufficient data"]
    fits: bool | None
    gap: float | None = None
    binding_point: dict[str, float | str] | None = None
    margin_class: str


class ChainringResult(BaseModel):
    fits: bool | None
    status: Literal["fit", "no-fit", "insufficient data"]
    pitch_diameter: float
    envelope_radius: float
    binding_radius: float | None = None
