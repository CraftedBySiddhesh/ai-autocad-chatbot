"""DXF authoring utilities for Stage 03."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal
from math import cos, pi, radians, sin
from pathlib import Path
from typing import Any, cast

import ezdxf

from .models import (
    DEFAULT_LAYER,
    Arc,
    Circle,
    Ellipse,
    Line,
    Point,
    Polyline,
    Rect,
    Text,
)

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

    def add_polyline(self, polyline: Polyline) -> None:
        points, closed, layer = polyline.as_dxf()
        if not points:
            return
        self.msp.add_lwpolyline(points, close=closed, dxfattribs={"layer": layer})

    def add_arc(self, arc: Arc) -> None:
        center, radius, start, end, layer = arc.as_dxf()
        self.msp.add_arc(center, radius, start, end, dxfattribs={"layer": layer})

    def add_ellipse(self, ellipse: Ellipse) -> None:
        center, rx, ry, rotation, layer = ellipse.as_dxf()
        if rx == 0:
            return
        ratio = ry / rx
        angle = radians(rotation)
        major_axis = (rx * cos(angle), rx * sin(angle))
        self.msp.add_ellipse(
            center=center,
            major_axis=major_axis,
            ratio=ratio,
            start_param=0.0,
            end_param=2 * pi,
            dxfattribs={"layer": layer},
        )

    def add_text(self, text: Text) -> None:
        content, position, height, layer = text.as_dxf()
        entity = cast(
            Any, self.msp.add_text(content, dxfattribs={"layer": layer, "height": height})
        )
        entity.set_pos(position)

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
