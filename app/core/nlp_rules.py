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
            r = float(to_mm(float(rad_num), rad_unit or "mm"))
        elif pre_num:
            r = float(to_mm(float(pre_num), pre_unit or "mm"))
        else:
            continue
        circles.append(CircleCmd(float(cx), float(cy), float(r)))

    # LINE
    for m in re.finditer(rf"\bline\s+from\s+{coord}\s+to\s+{coord}", t, flags=re.I):
        x1, y1, x2, y2 = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4))
        lines.append(LineCmd(x1, y1, x2, y2))

    rect_chunk_re = re.compile(
        r"\brectangle\b.*?(?=\b(?:circle|line|arc|polyline|ellipse|text|save|rectangle)\b|$)",
        flags=re.I | re.S,
    )
    width_re = re.compile(rf"\bwidth\s*{float_unit}", flags=re.I)
    height_re = re.compile(rf"\bheight\s*{float_unit}", flags=re.I)
    shorthand_re = re.compile(
        rf"{float_unit}\s*(?:x|×|by)\s*{float_unit}",
        flags=re.I,
    )
    center_re = re.compile(
        rf"(?:with\s+)?cent(?:er|re)(?:ed)?(?:\s+(?:at|on))?\s*{coord}",
        flags=re.I,
    )
    for rm in rect_chunk_re.finditer(t):
        chunk = rm.group(0)
        wmm: float | None = None
        hmm: float | None = None

        m_width = width_re.search(chunk)
        if m_width:
            w_val, w_unit = m_width.group(1), m_width.group(2)
            wmm = float(to_mm(float(w_val), w_unit or "mm"))

        m_height = height_re.search(chunk)
        if m_height:
            h_val, h_unit = m_height.group(1), m_height.group(2)
            hmm = float(to_mm(float(h_val), h_unit or "mm"))

        if wmm is None or hmm is None:
            m_sh = shorthand_re.search(chunk)
            if m_sh:
                w_val, w_unit, h_val, h_unit = (
                    m_sh.group(1),
                    m_sh.group(2),
                    m_sh.group(3),
                    m_sh.group(4),
                )
                if wmm is None:
                    wmm = float(to_mm(float(w_val), w_unit or "mm"))
                if hmm is None:
                    hmm = float(to_mm(float(h_val), h_unit or "mm"))

        wmm = wmm if wmm is not None else 100.0
        hmm = hmm if hmm is not None else 100.0

        anchor = "ll"
        x = 0.0
        y = 0.0

        m_center = center_re.search(chunk)
        chunk_for_at = chunk
        if m_center:
            anchor = "center"
            x = float(m_center.group(1))
            y = float(m_center.group(2))
            chunk_for_at = chunk[: m_center.start()] + chunk[m_center.end() :]

        if anchor == "ll":
            m_at = re.search(rf"\bat\s*{coord}", chunk_for_at, flags=re.I)
            if m_at:
                x = float(m_at.group(1))
                y = float(m_at.group(2))

        rects.append(RectCmd(x, y, wmm, hmm, anchor))

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
