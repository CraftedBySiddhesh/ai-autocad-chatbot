"""Regular expressions used by the deterministic mini-DSL parser."""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern


def _coord_pattern(prefix: str, allow_relative: bool = False) -> str:
    base = rf"\(\s*(?P<{prefix}x>-?\d+(?:\.\d+)?)\s*,\s*(?P<{prefix}y>-?\d+(?:\.\d+)?)\s*\)"
    if allow_relative:
        return rf"(?:(?P<{prefix}rel>rel(?:ative)?)\s*)?{base}"
    return base


@dataclass(frozen=True)
class Rule:
    name: str
    command: str
    pattern: Pattern[str]


# Canonical rules: 10 utterance templates that we guarantee to support deterministically.
RULES: list[Rule] = [
    Rule(
        name="circle_at",
        command="draw_circle",
        pattern=re.compile(
            rf"^\s*draw\s+circle\s+r\s*=\s*(?P<radius>-?\d+(?:\.\d+)?)\s+at\s+{_coord_pattern('center_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="circle_radius_center",
        command="draw_circle",
        pattern=re.compile(
            rf"^\s*draw\s+circle\s+radius\s*=\s*(?P<radius>-?\d+(?:\.\d+)?)\s+center\s+{_coord_pattern('center_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="circle_at_center",
        command="draw_circle",
        pattern=re.compile(
            rf"^\s*circle\s+radius\s+(?P<radius>-?\d+(?:\.\d+)?)\s+at\s+{_coord_pattern('center_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="line_from_to",
        command="draw_line",
        pattern=re.compile(
            rf"^\s*draw\s+line\s+from\s+{_coord_pattern('start_', allow_relative=True)}\s+to\s+{_coord_pattern('end_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="line_connect",
        command="draw_line",
        pattern=re.compile(
            rf"^\s*connect\s+{_coord_pattern('start_', allow_relative=True)}\s+to\s+{_coord_pattern('end_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="rect_at",
        command="draw_rect",
        pattern=re.compile(
            rf"^\s*draw\s+rect\s+w\s*=\s*(?P<width>-?\d+(?:\.\d+)?)\s+h\s*=\s*(?P<height>-?\d+(?:\.\d+)?)\s+at\s+{_coord_pattern('position_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="rect_corner",
        command="draw_rect",
        pattern=re.compile(
            rf"^\s*rect\s+w\s*=\s*(?P<width>-?\d+(?:\.\d+)?)\s+h\s*=\s*(?P<height>-?\d+(?:\.\d+)?)\s+corner\s+{_coord_pattern('position_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="rect_center",
        command="draw_rect",
        pattern=re.compile(
            rf"^\s*draw\s+rect\s+w\s*=\s*(?P<width>-?\d+(?:\.\d+)?)\s+h\s*=\s*(?P<height>-?\d+(?:\.\d+)?)\s+center\s+{_coord_pattern('position_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="rect_make_center",
        command="draw_rect",
        pattern=re.compile(
            rf"^\s*make\s+rectangle\s+w\s*=\s*(?P<width>-?\d+(?:\.\d+)?)\s+h\s*=\s*(?P<height>-?\d+(?:\.\d+)?)\s+center\s+{_coord_pattern('position_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
    Rule(
        name="rect_make_at",
        command="draw_rect",
        pattern=re.compile(
            rf"^\s*make\s+rectangle\s+w\s*=\s*(?P<width>-?\d+(?:\.\d+)?)\s+h\s*=\s*(?P<height>-?\d+(?:\.\d+)?)\s+at\s+{_coord_pattern('position_', allow_relative=True)}\s*$",
            flags=re.IGNORECASE,
        ),
    ),
]


COORDINATE_TOKEN = re.compile(r"^\s*\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\)\s*$")
RELATIVE_TOKEN = re.compile(
    r"^\s*rel(?:ative)?\s*\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\)\s*$", re.IGNORECASE
)


__all__ = ["RULES", "COORDINATE_TOKEN", "RELATIVE_TOKEN"]
