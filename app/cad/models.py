"""Basic 2D geometry models used by the DXF writer."""

from __future__ import annotations

from decimal import Decimal
from typing import Tuple

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_LAYER = "A-GEOM"


class Point(BaseModel):
    """2D coordinate expressed in millimetres."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    x: Decimal = Field(default=Decimal("0"))
    y: Decimal = Field(default=Decimal("0"))

    def as_tuple(self) -> Tuple[float, float]:
        return float(self.x), float(self.y)


class Line(BaseModel):
    start: Point
    end: Point
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[Tuple[float, float], Tuple[float, float], str]:
        return self.start.as_tuple(), self.end.as_tuple(), self.layer


class Circle(BaseModel):
    center: Point
    radius: Decimal = Field(gt=Decimal("0"))
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[Tuple[float, float], float, str]:
        return self.center.as_tuple(), float(self.radius), self.layer


class Rect(BaseModel):
    origin: Point
    width: Decimal = Field(gt=Decimal("0"))
    height: Decimal = Field(gt=Decimal("0"))
    layer: str = Field(default=DEFAULT_LAYER)

    def as_polyline(self) -> tuple[list[Tuple[float, float]], str]:
        ox, oy = self.origin.as_tuple()
        width = float(self.width)
        height = float(self.height)
        points = [
            (ox, oy),
            (ox + width, oy),
            (ox + width, oy + height),
            (ox, oy + height),
            (ox, oy),
        ]
        return points, self.layer
