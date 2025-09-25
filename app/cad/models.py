"""Basic 2D geometry models used by the DXF writer."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

DEFAULT_LAYER = "A-GEOM"


class Point(BaseModel):
    """2D coordinate expressed in millimetres."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    x: Decimal = Field(default=Decimal("0"))
    y: Decimal = Field(default=Decimal("0"))

    def as_tuple(self) -> tuple[float, float]:
        return float(self.x), float(self.y)


class Line(BaseModel):
    start: Point
    end: Point
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[tuple[float, float], tuple[float, float], str]:
        return self.start.as_tuple(), self.end.as_tuple(), self.layer


class Circle(BaseModel):
    center: Point
    radius: Decimal = Field(gt=Decimal("0"))
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[tuple[float, float], float, str]:
        return self.center.as_tuple(), float(self.radius), self.layer


class Rect(BaseModel):
    origin: Point
    width: Decimal = Field(gt=Decimal("0"))
    height: Decimal = Field(gt=Decimal("0"))
    layer: str = Field(default=DEFAULT_LAYER)

    def as_polyline(self) -> tuple[list[tuple[float, float]], str]:
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


class Polyline(BaseModel):
    points: list[Point]
    closed: bool = Field(default=False)
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[list[tuple[float, float]], bool, str]:
        return [p.as_tuple() for p in self.points], self.closed, self.layer


class Arc(BaseModel):
    center: Point
    radius: Decimal = Field(gt=Decimal("0"))
    start_angle: float = Field(default=0.0)
    end_angle: float = Field(default=360.0)
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[tuple[float, float], float, float, float, str]:
        return (
            self.center.as_tuple(),
            float(self.radius),
            float(self.start_angle),
            float(self.end_angle),
            self.layer,
        )


class Ellipse(BaseModel):
    center: Point
    rx: Decimal = Field(gt=Decimal("0"))
    ry: Decimal = Field(gt=Decimal("0"))
    rotation: float = Field(default=0.0)
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[tuple[float, float], float, float, float, str]:
        return (
            self.center.as_tuple(),
            float(self.rx),
            float(self.ry),
            float(self.rotation),
            self.layer,
        )


class Text(BaseModel):
    text: str
    position: Point
    height: Decimal = Field(gt=Decimal("0"))
    layer: str = Field(default=DEFAULT_LAYER)

    def as_dxf(self) -> tuple[str, tuple[float, float], float, str]:
        return self.text, self.position.as_tuple(), float(self.height), self.layer


class DrawingBundle(BaseModel):
    """Container used by the CLI to stage entities before writing."""

    circles: list[Circle] = Field(default_factory=list)
    lines: list[Line] = Field(default_factory=list)
    rects: list[Rect] = Field(default_factory=list)
    polylines: list[Polyline] = Field(default_factory=list)
    arcs: list[Arc] = Field(default_factory=list)
    ellipses: list[Ellipse] = Field(default_factory=list)
    texts: list[Text] = Field(default_factory=list)

    def extend(self, other: DrawingBundle) -> None:
        for attr in ("circles", "lines", "rects", "polylines", "arcs", "ellipses", "texts"):
            getattr(self, attr).extend(getattr(other, attr))

    def iter_all(self) -> Iterable[BaseModel]:  # pragma: no cover - utility helper
        for attr in ("circles", "lines", "rects", "polylines", "arcs", "ellipses", "texts"):
            yield from getattr(self, attr)
