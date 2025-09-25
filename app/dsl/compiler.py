"""Utilities that convert DSL commands into CAD primitives."""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from app.cad.models import Arc, Circle, DrawingBundle, Ellipse, Line, Point, Polyline, Rect, Text
from app.core.units import Unit, to_mm

from .commands import (
    CommandType,
    Coordinate,
    DrawArc,
    DrawCircle,
    DrawEllipse,
    DrawLine,
    DrawPolyline,
    DrawRect,
    DrawText,
)

_DEFAULT_VALUES = {
    "circle.radius": Decimal("10"),
    "rect.width": Decimal("100"),
    "rect.height": Decimal("100"),
    "arc.radius": Decimal("10"),
    "ellipse.rx": Decimal("25"),
    "ellipse.ry": Decimal("15"),
    "text.height": Decimal("5"),
}


class CommandCompiler:
    """Compile parsed command models into CAD primitives."""

    def __init__(self, *, default_unit: Unit = Unit.MILLIMETER) -> None:
        self.default_unit = default_unit
        self._cursor = Point(x=Decimal("0"), y=Decimal("0"))

    def _to_mm(self, value: float | int | Decimal | None, unit: str | None) -> Decimal:
        if value is None:
            raise ValueError("Missing numeric value")
        resolved_unit = unit or self.default_unit.value
        return to_mm(value, resolved_unit)

    def _coordinate(self, coord: Coordinate, *, update_cursor: bool = True) -> Point:
        x_val = coord.x if coord.x is not None else 0.0
        y_val = coord.y if coord.y is not None else 0.0
        unit = coord.unit or self.default_unit.value
        x_mm = to_mm(x_val, unit)
        y_mm = to_mm(y_val, unit)

        if coord.system == "relative":
            point = Point(x=self._cursor.x + x_mm, y=self._cursor.y + y_mm)
        else:
            point = Point(x=x_mm, y=y_mm)

        if update_cursor:
            self._cursor = point
        return point

    def _radius(self, radius: float | None, unit: str | None, *, field: str) -> Decimal:
        if radius is None:
            return _DEFAULT_VALUES[field]
        return self._to_mm(radius, unit)

    def _dimension(self, value: float | None, unit: str | None, *, field: str) -> Decimal:
        if value is None:
            return _DEFAULT_VALUES[field]
        return self._to_mm(value, unit)

    def compile(self, commands: Iterable[CommandType]) -> DrawingBundle:
        bundle = DrawingBundle()

        for command in commands:
            if isinstance(command, DrawCircle):
                radius = self._radius(command.radius, command.radius_unit, field="circle.radius")
                center = self._coordinate(command.center)
                bundle.circles.append(Circle(center=center, radius=radius))
            elif isinstance(command, DrawLine):
                start = self._coordinate(command.start)
                end = self._coordinate(command.end)
                bundle.lines.append(Line(start=start, end=end))
            elif isinstance(command, DrawRect):
                width = self._dimension(command.width, command.width_unit, field="rect.width")
                height = self._dimension(command.height, command.height_unit, field="rect.height")
                position = self._coordinate(command.position)
                if command.anchor == "center":
                    origin = Point(x=position.x - width / 2, y=position.y - height / 2)
                else:
                    origin = position
                bundle.rects.append(Rect(origin=origin, width=width, height=height))
            elif isinstance(command, DrawPolyline):
                points: list[Point] = []
                for coord in command.points:
                    points.append(self._coordinate(coord))
                if points:
                    bundle.polylines.append(Polyline(points=points, closed=command.closed))
            elif isinstance(command, DrawArc):
                radius = self._radius(command.radius, command.radius_unit, field="arc.radius")
                center = self._coordinate(command.center)
                start_angle = command.start_angle if command.start_angle is not None else 0.0
                end_angle = command.end_angle if command.end_angle is not None else 360.0
                bundle.arcs.append(
                    Arc(center=center, radius=radius, start_angle=start_angle, end_angle=end_angle)
                )
            elif isinstance(command, DrawEllipse):
                rx = self._dimension(command.rx, command.rx_unit, field="ellipse.rx")
                ry = self._dimension(command.ry, command.ry_unit, field="ellipse.ry")
                center = self._coordinate(command.center)
                bundle.ellipses.append(
                    Ellipse(center=center, rx=rx, ry=ry, rotation=command.rotation or 0.0)
                )
            elif isinstance(command, DrawText):
                position = self._coordinate(command.position)
                height = self._dimension(command.height, command.height_unit, field="text.height")
                bundle.texts.append(Text(text=command.text, position=position, height=height))

        return bundle


__all__ = ["CommandCompiler"]
