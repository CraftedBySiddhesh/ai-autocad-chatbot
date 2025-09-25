from __future__ import annotations

from pathlib import Path

import ezdxf

from app.cad.models import Circle, Line, Point, Rect
from app.cad.writer import DxfWriter


def test_writer_adds_entities(tmp_path: Path) -> None:
    writer = DxfWriter()
    writer.add_line(Line(start=Point(x=0, y=0), end=Point(x=100, y=0)))
    writer.add_circle(Circle(center=Point(x=50, y=50), radius=25))
    writer.add_rect(Rect(origin=Point(x=0, y=0), width=100, height=50))

    output_path = writer.save(tmp_path / "test_stage3.dxf")
    assert output_path.exists()

    doc = ezdxf.readfile(output_path)
    msp = doc.modelspace()
    assert doc.layers.has_entry("A-GEOM")
    assert len(msp.query("LINE")) == 1
    assert len(msp.query("CIRCLE")) == 1
    assert len(msp.query("LWPOLYLINE")) == 1
