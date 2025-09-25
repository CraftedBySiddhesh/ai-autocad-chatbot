"""Utilities for unit conversion using :class:`~decimal.Decimal`."""

from __future__ import annotations

import re
from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal, getcontext
from enum import Enum

MM_PER_INCH = Decimal("25.4")
MM_PRECISION = Decimal("0.000001")

getcontext().prec = 28


class Unit(str, Enum):
    """Supported length units."""

    MILLIMETER = "mm"
    INCH = "in"

    @classmethod
    def from_string(cls, value: str | None, default: Unit | None = None) -> Unit:
        if value is None or not value.strip():
            return default or cls.MILLIMETER
        normalized = value.strip().lower()
        for unit, aliases in _ALIASES.items():
            if normalized in aliases:
                return unit
        raise ValueError(f"Unsupported unit '{value}'")


_ALIASES: dict[Unit, set[str]] = {
    Unit.MILLIMETER: {"mm", "millimeter", "millimeters", "millimetre", "millimetres"},
    Unit.INCH: {"in", "inch", "inches", '"'},
}

_LENGTH_RE = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*([a-z\"]+)?\s*$", re.IGNORECASE)


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(MM_PRECISION, rounding=ROUND_HALF_UP)


def _resolve_default_unit() -> Unit:
    from .config import get_settings

    settings = get_settings()
    return Unit.from_string(settings.DEFAULT_UNITS, default=Unit.MILLIMETER)


def _resolve_unit(unit: Unit | str | None, fallback: Unit | None = None) -> Unit:
    if isinstance(unit, Unit):
        return unit
    return Unit.from_string(
        unit if unit is None or isinstance(unit, str) else str(unit), default=fallback
    )


def parse_length(text: str, *, default_unit: Unit | None = None) -> Decimal:
    match = _LENGTH_RE.match(text)
    if not match:
        raise ValueError(f"Could not parse length expression '{text}'")
    magnitude = Decimal(match.group(1))
    unit = _resolve_unit(match.group(2), fallback=default_unit or _resolve_default_unit())
    return to_mm(magnitude, unit=unit)


def to_mm(value: float | int | Decimal, unit: Unit | str | None) -> Decimal:
    unit_enum = _resolve_unit(unit, fallback=_resolve_default_unit())
    decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    if unit_enum == Unit.INCH:
        return _quantize(decimal_value * MM_PER_INCH)
    return _quantize(decimal_value)


def from_mm(value: float | int | Decimal, unit: Unit | str | None) -> Decimal:
    unit_enum = _resolve_unit(unit, fallback=_resolve_default_unit())
    decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    if unit_enum == Unit.INCH:
        return _quantize(decimal_value / MM_PER_INCH)
    if unit_enum == Unit.MILLIMETER:
        return _quantize(decimal_value)
    raise ValueError(f"Unsupported unit '{unit_enum}'")


def convert_length(
    value: float | int | Decimal, from_unit: Unit | str, to_unit: Unit | str
) -> Decimal:
    mm_value = to_mm(value, from_unit)
    return from_mm(mm_value, to_unit)


def available_units() -> Iterable[str]:
    return sorted({alias for aliases in _ALIASES.values() for alias in aliases})
