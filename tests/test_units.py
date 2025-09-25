from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.config import Settings, reload_settings
from app.core.units import Unit, convert_length, from_mm, parse_length, to_mm


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        (Decimal("0"), Unit.MILLIMETER, Decimal("0")),
        (Decimal("25.4"), Unit.MILLIMETER, Decimal("25.4")),
        (Decimal("1"), Unit.INCH, Decimal("25.4")),
        (Decimal("-2"), Unit.INCH, Decimal("-50.8")),
    ],
)
def test_to_mm(value: Decimal, unit: Unit, expected: Decimal) -> None:
    assert to_mm(value, unit) == expected


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [
        (Decimal("25.4"), Unit.INCH, Decimal("1")),
        (Decimal("50.8"), Unit.INCH, Decimal("2")),
        (Decimal("12.7"), Unit.MILLIMETER, Decimal("12.7")),
    ],
)
def test_from_mm(value: Decimal, unit: Unit, expected: Decimal) -> None:
    assert from_mm(value, unit) == expected


@pytest.mark.parametrize(
    ("value", "from_unit", "to_unit", "expected"),
    [
        (Decimal("100"), Unit.MILLIMETER, Unit.MILLIMETER, Decimal("100")),
        (Decimal("2"), Unit.INCH, Unit.MILLIMETER, Decimal("50.8")),
        (Decimal("100"), Unit.MILLIMETER, Unit.INCH, Decimal("3.937008")),
    ],
)
def test_convert_length(value: Decimal, from_unit: Unit, to_unit: Unit, expected: Decimal) -> None:
    assert convert_length(value, from_unit, to_unit) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("50 mm", Decimal("50")),
        ("2 in", Decimal("50.8")),
        ("2", Decimal("2")),
        ("-3 in", Decimal("-76.2")),
    ],
)
def test_parse_length(text: str, expected: Decimal) -> None:
    assert parse_length(text) == expected


def test_settings_alias(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEFAULT_UNITS", "in")
    settings = Settings()
    assert settings.DEFAULT_UNITS == "in"


def test_parse_length_respects_env_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DEFAULT_UNITS", "in")
    reload_settings()
    try:
        assert parse_length("2") == Decimal("50.8")
    finally:
        monkeypatch.delenv("DEFAULT_UNITS", raising=False)
        reload_settings()
