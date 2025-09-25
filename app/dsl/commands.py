"""Pydantic command models used by rule and LLM parsers."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Coordinate(BaseModel):
    """Represents either an absolute or relative coordinate pair."""

    model_config = ConfigDict(extra="forbid")

    x: float | None = Field(default=None, description="X component of the coordinate")
    y: float | None = Field(default=None, description="Y component of the coordinate")
    system: Literal["absolute", "relative"] = Field(
        default="absolute",
        description="Whether the coordinate is absolute (global) or relative to the active cursor",
    )
    unit: Literal["mm", "in"] | None = Field(
        default=None, description="Optional unit used by the coordinate components."
    )

    @field_validator("system")
    @classmethod
    def _normalise_system(cls, value: str) -> str:
        return value.lower()


class Command(BaseModel):
    """Base command model."""

    model_config = ConfigDict(extra="forbid")


class DrawCircle(Command):
    type: Literal["draw_circle"] = "draw_circle"
    center: Coordinate = Field(default_factory=Coordinate)
    radius: float | None = Field(default=None, ge=0, description="Radius value")
    radius_unit: Literal["mm", "in"] | None = Field(
        default=None, description="Unit associated with the radius if provided"
    )


class DrawLine(Command):
    type: Literal["draw_line"] = "draw_line"
    start: Coordinate = Field(default_factory=Coordinate)
    end: Coordinate = Field(default_factory=Coordinate)


class DrawRect(Command):
    type: Literal["draw_rect"] = "draw_rect"
    anchor: Literal["corner", "center"] = Field(
        default="corner",
        description="The semantic meaning of `position` (lower-left corner or centre).",
    )
    position: Coordinate = Field(default_factory=Coordinate)
    width: float | None = Field(default=None, ge=0)
    width_unit: Literal["mm", "in"] | None = Field(default=None)
    height: float | None = Field(default=None, ge=0)
    height_unit: Literal["mm", "in"] | None = Field(default=None)


class DrawPolyline(Command):
    type: Literal["draw_polyline"] = "draw_polyline"
    points: list[Coordinate] = Field(default_factory=list)
    closed: bool = Field(default=False)


class DrawArc(Command):
    type: Literal["draw_arc"] = "draw_arc"
    center: Coordinate = Field(default_factory=Coordinate)
    radius: float | None = Field(default=None, ge=0)
    radius_unit: Literal["mm", "in"] | None = Field(default=None)
    start_angle: float | None = Field(default=None, description="Start angle in degrees")
    end_angle: float | None = Field(default=None, description="End angle in degrees")


class DrawEllipse(Command):
    type: Literal["draw_ellipse"] = "draw_ellipse"
    center: Coordinate = Field(default_factory=Coordinate)
    rx: float | None = Field(default=None, ge=0)
    rx_unit: Literal["mm", "in"] | None = Field(default=None)
    ry: float | None = Field(default=None, ge=0)
    ry_unit: Literal["mm", "in"] | None = Field(default=None)
    rotation: float | None = Field(default=0.0, description="Rotation in degrees")


class DrawText(Command):
    type: Literal["draw_text"] = "draw_text"
    text: str = Field(default="", description="Label contents")
    position: Coordinate = Field(default_factory=Coordinate)
    height: float | None = Field(default=None, ge=0)
    height_unit: Literal["mm", "in"] | None = Field(default=None)


CommandType = Annotated[
    DrawCircle | DrawLine | DrawRect | DrawPolyline | DrawArc | DrawEllipse | DrawText,
    Field(discriminator="type"),
]


class CommandList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commands: list[CommandType]
