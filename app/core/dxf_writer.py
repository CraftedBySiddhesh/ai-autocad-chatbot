from math import pi
from pathlib import Path

import ezdxf

from .nlp_rules import Program


def render(program: Program, out_path: str | None = None) -> str:
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()

    for name, color in [
        ("CIRCLES", 1),
        ("LINES", 3),
        ("RECTS", 5),
        ("ARCS", 2),
        ("PLINES", 4),
        ("ELLIPSES", 6),
        ("TEXTS", 7),
    ]:
        if name not in doc.layers:
            doc.layers.add(name, color=color)

    for c in program.circles:
        msp.add_circle((c.x, c.y), c.r, dxfattribs={"layer": "CIRCLES"})
    for line in program.lines:
        msp.add_line((line.x1, line.y1), (line.x2, line.y2), dxfattribs={"layer": "LINES"})
    for r in program.rects:
        msp.add_lwpolyline(
            [(r.x, r.y), (r.x + r.w, r.y), (r.x + r.w, r.y + r.h), (r.x, r.y + r.h), (r.x, r.y)],
            close=True,
            dxfattribs={"layer": "RECTS"},
        )
    for a in program.arcs:
        msp.add_arc((a.x, a.y), a.r, a.a1, a.a2, dxfattribs={"layer": "ARCS"})
    for pl in program.polylines:
        pts = list(pl.pts)
        if pl.closed and pts and pts[0] != pts[-1]:
            pts.append(pts[0])
        msp.add_lwpolyline(pts, close=pl.closed, dxfattribs={"layer": "PLINES"})
    for e in program.ellipses:
        ratio = e.ry / e.rx if e.rx != 0 else 1.0
        msp.add_ellipse(
            center=(e.x, e.y),
            major_axis=(e.rx, 0),
            ratio=ratio,
            start_param=0.0,
            end_param=2 * pi,
            dxfattribs={"layer": "ELLIPSES"},
        )
    for tx in program.texts:
        msp.add_text(tx.text, dxfattribs={"height": tx.height, "layer": "TEXTS"}).set_pos(
            (tx.x, tx.y)
        )

    # Output path
    if out_path:
        path = Path(out_path)
    elif program.save:
        path = Path(program.save.path)
    else:
        path = Path("outputs/out.dxf")

    if not path.is_absolute():
        path = Path("outputs") / path.name
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.saveas(path)
    return str(path.resolve())
