import pytest

from app.dsl.commands import Coordinate, DrawCircle, DrawLine, DrawRect
from app.dsl.errors import E_COORDINATE_SYNTAX, ParseError
from app.dsl.parse_rule import parse_rule

CANONICAL_CASES = [
    (
        "draw circle r=50 at (100,100)",
        DrawCircle(radius=50.0, center=Coordinate(x=100.0, y=100.0)),
    ),
    (
        "draw circle radius=25 center rel(10,-5)",
        DrawCircle(radius=25.0, center=Coordinate(x=10.0, y=-5.0, system="relative")),
    ),
    (
        "circle radius 40 at relative (0,0)",
        DrawCircle(radius=40.0, center=Coordinate(x=0.0, y=0.0, system="relative")),
    ),
    (
        "draw line from (0,0) to (100,0)",
        DrawLine(
            start=Coordinate(x=0.0, y=0.0),
            end=Coordinate(x=100.0, y=0.0),
        ),
    ),
    (
        "draw line from rel(0,0) to (25,25)",
        DrawLine(
            start=Coordinate(x=0.0, y=0.0, system="relative"),
            end=Coordinate(x=25.0, y=25.0),
        ),
    ),
    (
        "connect (5,5) to rel(10,10)",
        DrawLine(
            start=Coordinate(x=5.0, y=5.0),
            end=Coordinate(x=10.0, y=10.0, system="relative"),
        ),
    ),
    (
        "draw rect w=20 h=30 at (0,0)",
        DrawRect(
            width=20.0,
            height=30.0,
            position=Coordinate(x=0.0, y=0.0),
            anchor="corner",
        ),
    ),
    (
        "draw rect w=20 h=30 center (10,10)",
        DrawRect(
            width=20.0,
            height=30.0,
            position=Coordinate(x=10.0, y=10.0),
            anchor="center",
        ),
    ),
    (
        "make rectangle w=20 h=30 at relative (5,5)",
        DrawRect(
            width=20.0,
            height=30.0,
            position=Coordinate(x=5.0, y=5.0, system="relative"),
            anchor="corner",
        ),
    ),
    (
        "make rectangle w=20 h=30 center rel(0,-10)",
        DrawRect(
            width=20.0,
            height=30.0,
            position=Coordinate(x=0.0, y=-10.0, system="relative"),
            anchor="center",
        ),
    ),
]


def test_canonical_sentences_cover_all_rules():
    for sentence, expected in CANONICAL_CASES:
        commands = parse_rule(sentence)
        assert len(commands) == 1
        assert commands[0].model_dump() == expected.model_dump()


def test_multiple_sentences_split():
    combo = (
        "draw circle r=50 at (100,100) and "
        "draw line from (0,0) to (10,10) and "
        "draw rect w=20 h=30 at (0,0)"
    )
    commands = parse_rule(combo)
    assert len(commands) == 3


def test_invalid_coordinate_error():
    with pytest.raises(ParseError) as exc:
        parse_rule("draw circle r=50 at (10,abc)")
    assert exc.value.code == E_COORDINATE_SYNTAX[0]
