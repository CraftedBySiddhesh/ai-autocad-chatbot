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
    radius: float | None = Field(default=None, ge=0, description="Radius in drawing units")


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
    height: float | None = Field(default=None, ge=0)


CommandType = Annotated[
    DrawCircle | DrawLine | DrawRect,
    Field(discriminator="type"),
]


class CommandList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commands: list[CommandType]
