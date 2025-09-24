from dataclasses import dataclass
import re

from .units import to_mm


@dataclass
class CircleCmd:
    x: float
    y: float
    r: float


@dataclass
class LineCmd:
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class RectCmd:
    x: float
    y: float
    w: float
    h: float
    anchor: str = "ll"


@dataclass
class ArcCmd:
    x: float
    y: float
    r: float
    a1: float
    a2: float


@dataclass
class PolylineCmd:
    pts: list[tuple[float, float]]
    closed: bool = False


@dataclass
class EllipseCmd:
    x: float
    y: float
    rx: float
    ry: float
    rot_deg: float = 0.0  # simple rotation support


@dataclass
class TextCmd:
    x: float
    y: float
    text: str
    height: float = 100.0  # mm


@dataclass
class SaveCmd:
    path: str


@dataclass
class Program:
    circles: list[CircleCmd]
    lines: list[LineCmd]
    rects: list[RectCmd]
    arcs: list[ArcCmd]
    polylines: list[PolylineCmd]
    ellipses: list[EllipseCmd]
    texts: list[TextCmd]
    save: SaveCmd | None


coord = r"\(?\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)?"
unit_word = r"(?:mm|millimeters?|inch(?:es)?|in|cm|centimeters?|m|meters?)"
float_unit = rf"(-?\d+(?:\.\d+)?)(?:\s*({unit_word}))?"


def _split_points(blob: str) -> list[tuple[float, float]]:
    # Accept "0,0  10,20  30,40" or "(0,0) (10,20) (30,40)"
    pts = []
    for m in re.finditer(coord, blob):
        pts.append((float(m.group(1)), float(m.group(2))))
    return pts


def parse(text: str) -> Program:
    t = " " + text.strip() + " "
    t = re.sub(r"[;\n]+", " and ", t, flags=re.I)

    circles: list[CircleCmd] = []
    lines: list[LineCmd] = []
    rects: list[RectCmd] = []
    arcs: list[ArcCmd] = []
    polylines: list[PolylineCmd] = []
    ellipses: list[EllipseCmd] = []
    texts: list[TextCmd] = []
    save: SaveCmd | None = None

    # SAVE
    m = re.search(r"save\s+as\s+([^\s]+\.dxf)", t, flags=re.I)
    if m:
        save = SaveCmd(m.group(1))

    # CIRCLE: "<num><unit> circle ... at (x,y)" OR "circle radius <num><unit> ... at (x,y)"
    for m in re.finditer(
        rf"(?:\b(\d+(?:\.\d+)?)\s*({unit_word})\s*circle\b|\bcircle\b.*?\bradius\s*{float_unit})"
        rf".*?(?:at|center)\s*{coord}",
        t,
        flags=re.I,
    ):
        pre_num, pre_unit, rad_num, rad_unit, cx, cy = (
            m.group(1),
            m.group(2),
            m.group(3),
            m.group(4),
            m.group(5),
            m.group(6),
        )
        if rad_num:
            r = to_mm(float(rad_num), rad_unit or "mm")
        elif pre_num:
            r = to_mm(float(pre_num), pre_unit or "mm")
        else:
            continue
        circles.append(CircleCmd(float(cx), float(cy), float(r)))

    # LINE
    for m in re.finditer(rf"\bline\s+from\s+{coord}\s+to\s+{coord}", t, flags=re.I):
        x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
        lines.append(LineCmd(x1, y1, x2, y2))

    # RECT with defaults if missing w/h
    for m in re.finditer(
        rf"\brectangle\b(?:.*?\bwidth\s*{float_unit})?(?:.*?\bheight\s*{float_unit})?(?:.*?\bat\s*{coord})?",
        t,
        flags=re.I,
    ):
        # width/height capture order: w_val,w_unit,h_val,h_unit,(x,y)
        groups = m.groups()
        w_val = groups[0]
        w_unit = groups[1]
        h_val = groups[2]
        h_unit = groups[3]
        x = groups[4]
        y = groups[5]
        wmm = to_mm(float(w_val), w_unit or "mm") if w_val else 100.0
        hmm = to_mm(float(h_val), h_unit or "mm") if h_val else 100.0
        xx = float(x) if x else 0.0
        yy = float(y) if y else 0.0
        rects.append(RectCmd(xx, yy, wmm, hmm))

    # ARC: "arc radius <num><unit> at (cx,cy) from <a1> to <a2>" (degrees)
    for m in re.finditer(
        rf"\barc\b.*?\bradius\s*{float_unit}.*?\bat\s*{coord}.*?\bfrom\s*(-?\d+(?:\.\d+)?)\s*\bto\s*(-?\d+(?:\.\d+)?)",
        t,
        flags=re.I,
    ):
        r_val, r_unit, cx, cy, a1, a2 = (
            m.group(1),
            (m.group(2) or "mm"),
            m.group(3),
            m.group(4),
            m.group(5),
            m.group(6),
        )
        arcs.append(ArcCmd(float(cx), float(cy), to_mm(float(r_val), r_unit), float(a1), float(a2)))

    # POLYLINE: "polyline points: (0,0) (10,20) (30,40)" or "polyline closed points: ..."
    for m in re.finditer(
        r"\bpolyline\b\s*(closed)?\s*points?:\s*([^\n]+?)(?=\band\b|\bsave\b|$)", t, flags=re.I
    ):
        closed = bool(m.group(1))
        pts = _split_points(m.group(2))
        if pts:
            polylines.append(PolylineCmd(pts, closed))

    # ELLIPSE: "ellipse center (x,y) rx <num><unit> ry <num><unit> [rot <deg>]"
    for m in re.finditer(
        rf"\bellipse\b.*?\bcenter\s*{coord}.*?\brx\s*{float_unit}.*?\bry\s*{float_unit}(?:.*?\brot\s*(-?\d+(?:\.\d+)?))?",
        t,
        flags=re.I,
    ):
        cx, cy = float(m.group(1)), float(m.group(2))
        rx_val, rx_unit = float(m.group(3)), (m.group(4) or "mm")
        ry_val, ry_unit = float(m.group(5)), (m.group(6) or "mm")
        rot = float(m.group(7)) if m.group(7) else 0.0
        ellipses.append(EllipseCmd(cx, cy, to_mm(rx_val, rx_unit), to_mm(ry_val, ry_unit), rot))

    # TEXT: 'text "Hello" at (x,y) [height <num><unit>]'
    for m in re.finditer(
        rf'\btext\s+"([^"]+)"\s*\bat\s*{coord}(?:.*?\bheight\s*{float_unit})?', t, flags=re.I
    ):
        s, x, y = m.group(1), float(m.group(2)), float(m.group(3))
        h_val, h_unit = m.group(4), (m.group(5) or "mm")
        height = to_mm(float(h_val), h_unit) if h_val else 100.0
        texts.append(TextCmd(x, y, s, height))

    return Program(
        circles=circles,
        lines=lines,
        rects=rects,
        arcs=arcs,
        polylines=polylines,
        ellipses=ellipses,
        texts=texts,
        save=save,
    )
