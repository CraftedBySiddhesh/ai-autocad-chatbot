"""Helpers for translating legacy rule parser output into CAD primitives."""

from __future__ import annotations

from decimal import Decimal

from app.cad.models import Arc, Circle, DrawingBundle, Ellipse, Line, Point, Polyline, Rect, Text

from .nlp_rules import Program


def _point(x: float, y: float) -> Point:
    return Point(x=Decimal(str(x)), y=Decimal(str(y)))


def program_to_bundle(program: Program) -> DrawingBundle:
    bundle = DrawingBundle()

    for circle in program.circles:
        bundle.circles.append(
            Circle(center=_point(circle.x, circle.y), radius=Decimal(str(circle.r)))
        )

    for line in program.lines:
        bundle.lines.append(Line(start=_point(line.x1, line.y1), end=_point(line.x2, line.y2)))

    for rect in program.rects:
        if rect.anchor == "center":
            origin_x = rect.x - rect.w / 2
            origin_y = rect.y - rect.h / 2
        else:
            origin_x = rect.x
            origin_y = rect.y
        bundle.rects.append(
            Rect(
                origin=_point(origin_x, origin_y),
                width=Decimal(str(rect.w)),
                height=Decimal(str(rect.h)),
            )
        )

    for arc in program.arcs:
        bundle.arcs.append(
            Arc(
                center=_point(arc.x, arc.y),
                radius=Decimal(str(arc.r)),
                start_angle=float(arc.a1),
                end_angle=float(arc.a2),
            )
        )

    for polyline in program.polylines:
        points = [_point(x, y) for x, y in polyline.pts]
        bundle.polylines.append(Polyline(points=points, closed=polyline.closed))

    for ellipse in program.ellipses:
        bundle.ellipses.append(
            Ellipse(
                center=_point(ellipse.x, ellipse.y),
                rx=Decimal(str(ellipse.rx)),
                ry=Decimal(str(ellipse.ry)),
                rotation=float(ellipse.rot_deg),
            )
        )

    for text in program.texts:
        bundle.texts.append(
            Text(
                text=text.text,
                position=_point(text.x, text.y),
                height=Decimal(str(text.height)),
            )
        )

    return bundle


__all__ = ["program_to_bundle"]
