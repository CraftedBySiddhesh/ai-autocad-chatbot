INCH_TO_MM = 25.4


def to_mm(value: float, unit: str | None) -> float:
    if unit is None or unit.lower() in {"mm", "millimeter", "millimeters"}:
        return float(value)
    if unit.lower() in {"inch", "inches", "in"}:
        return float(value) * INCH_TO_MM
    if unit.lower() in {"cm", "centimeter", "centimeters"}:
        return float(value) * 10.0
    if unit.lower() in {"m", "meter", "meters"}:
        return float(value) * 1000.0
    return float(value)
