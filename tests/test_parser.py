from app.core.nlp_rules import parse


def test_circle_inch():
    p = parse("draw a 2 inch circle at (0,0)")
    assert len(p.circles) == 1
    assert round(p.circles[0].r, 1) == 50.8


def test_line():
    p = parse("draw a line from 0,0 to 100,50")
    assert len(p.lines) == 1


def test_rect_defaults():
    p = parse("draw a rectangle at (10,10)")
    assert len(p.rects) == 1
    r = p.rects[0]
    assert r.w == 100.0 and r.h == 100.0 and r.x == 10 and r.y == 10


def test_arc():
    p = parse("draw an arc radius 40 mm at (0,0) from 0 to 90")
    assert len(p.arcs) == 1
    a = p.arcs[0]
    assert a.r == 40 and a.a1 == 0 and a.a2 == 90


def test_polyline_open():
    p = parse("polyline points: (0,0) (10,0) (10,10)")
    assert len(p.polylines) == 1
    assert p.polylines[0].closed is False
    assert len(p.polylines[0].pts) == 3


def test_polyline_closed():
    p = parse("polyline closed points: 0,0 10,0 10,10 0,10")
    assert len(p.polylines) == 1
    assert p.polylines[0].closed is True
    assert len(p.polylines[0].pts) == 4


def test_ellipse():
    p = parse("ellipse center (0,0) rx 40 mm ry 20 mm rot 15")
    assert len(p.ellipses) == 1
    e = p.ellipses[0]
    assert e.rx == 40 and e.ry == 20 and e.rot_deg == 15


def test_text():
    p = parse("text \"Kitchen\" at (100,200) height 50 mm")
    assert len(p.texts) == 1
    t = p.texts[0]
    assert t.text == "Kitchen" and t.height == 50.0
