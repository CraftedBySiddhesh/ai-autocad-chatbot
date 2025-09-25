"""DXF authoring utilities for Stage 03."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from pathlib import Path

import ezdxf

from .models import DEFAULT_LAYER, Circle, Line, Point, Rect

DXF_VERSION = "R2018"


class DxfWriter:
    """Incrementally build a DXF document."""

    def __init__(self) -> None:
        self.doc = ezdxf.new(DXF_VERSION)
        self.msp = self.doc.modelspace()
        self._ensure_layers([DEFAULT_LAYER])

    def _ensure_layers(self, layers: Iterable[str]) -> None:
        for layer in layers:
            if layer not in self.doc.layers:
                self.doc.layers.add(layer)

    def add_line(self, line: Line) -> None:
        start, end, layer = line.as_dxf()
        self.msp.add_line(start, end, dxfattribs={"layer": layer})

    def add_circle(self, circle: Circle) -> None:
        center, radius, layer = circle.as_dxf()
        self.msp.add_circle(center, radius, dxfattribs={"layer": layer})

    def add_rect(self, rect: Rect) -> None:
        points, layer = rect.as_polyline()
        self.msp.add_lwpolyline(points, close=True, dxfattribs={"layer": layer})

    def save(self, path: str | Path) -> Path:
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.saveas(output_path)
        return output_path.resolve()


def demo(path: str | Path) -> Path:
    writer = DxfWriter()
    writer.add_line(
        Line(
            start=Point(x=Decimal("0"), y=Decimal("0")),
            end=Point(x=Decimal("100"), y=Decimal("0")),
        )
    )
    writer.add_circle(Circle(center=Point(x=Decimal("50"), y=Decimal("50")), radius=Decimal("25")))
    writer.add_rect(
        Rect(
            origin=Point(x=Decimal("-25"), y=Decimal("-25")),
            width=Decimal("50"),
            height=Decimal("40"),
        )
    )
    return writer.save(path)
