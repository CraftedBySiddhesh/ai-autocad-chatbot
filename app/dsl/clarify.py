"""Clarification engine for filling incomplete command data."""
from __future__ import annotations

from typing import Any, Iterable, List

from pydantic import BaseModel, ConfigDict

from .commands import CommandType, DrawCircle, DrawLine, DrawRect
from app.memory.session import SessionMemory

_USE_PREVIOUS = {"use previous value", "previous", "same", "last", "prior"}


class FollowUpQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    command_index: int
    field: str
    prompt: str
    expected: str = "number"


class ReadyCommands(BaseModel):
    model_config = ConfigDict(extra="forbid")

    commands: List[CommandType]


def _normalise_answer(answer: Any) -> Any:
    if isinstance(answer, str):
        stripped = answer.strip().lower()
        if stripped in _USE_PREVIOUS:
            return "__USE_PREVIOUS__"
        try:
            return float(answer)
        except ValueError:
            return answer
    return answer


def _resolve_numeric(
    session: SessionMemory,
    command_index: int,
    key: str,
    current: Any,
    prompt: str,
    followups: List[FollowUpQuestion],
) -> float | None:
    if current is not None:
        value = float(current)
        session.remember_default(key, value)
        return value

    answer_key = f"answer.{command_index}.{key}"
    answer = session.pop(answer_key)
    if answer is not None:
        normalised = _normalise_answer(answer)
        if normalised == "__USE_PREVIOUS__":
            default = session.get_default(key)
            if default is not None:
                return float(default)
        else:
            try:
                value = float(normalised)
            except (TypeError, ValueError):
                followups.append(
                    FollowUpQuestion(
                        id=answer_key,
                        command_index=command_index,
                        field=key,
                        prompt=f"{prompt} (could not interpret '{answer}')",
                    )
                )
                return None
            session.remember_default(key, value)
            return value

    default = session.get_default(key)
    if default is not None:
        return float(default)

    followups.append(
        FollowUpQuestion(
            id=answer_key,
            command_index=command_index,
            field=key,
            prompt=prompt,
        )
    )
    return None


def _clarify_circle(index: int, cmd: DrawCircle, session: SessionMemory, followups: List[FollowUpQuestion]) -> DrawCircle:
    radius = _resolve_numeric(session, index, "circle.radius", cmd.radius, "What radius should the circle have?", followups)

    center_x = _resolve_numeric(
        session,
        index,
        "circle.center.x",
        cmd.center.x,
        "Provide the circle centre X coordinate.",
        followups,
    )
    center_y = _resolve_numeric(
        session,
        index,
        "circle.center.y",
        cmd.center.y,
        "Provide the circle centre Y coordinate.",
        followups,
    )

    new_center = cmd.center.model_copy(update={"x": center_x, "y": center_y})
    return cmd.model_copy(update={"radius": radius, "center": new_center})


def _clarify_line(index: int, cmd: DrawLine, session: SessionMemory, followups: List[FollowUpQuestion]) -> DrawLine:
    start_x = _resolve_numeric(
        session,
        index,
        "line.start.x",
        cmd.start.x,
        "Provide the line start X coordinate.",
        followups,
    )
    start_y = _resolve_numeric(
        session,
        index,
        "line.start.y",
        cmd.start.y,
        "Provide the line start Y coordinate.",
        followups,
    )
    end_x = _resolve_numeric(
        session,
        index,
        "line.end.x",
        cmd.end.x,
        "Provide the line end X coordinate.",
        followups,
    )
    end_y = _resolve_numeric(
        session,
        index,
        "line.end.y",
        cmd.end.y,
        "Provide the line end Y coordinate.",
        followups,
    )

    return cmd.model_copy(
        update={
            "start": cmd.start.model_copy(update={"x": start_x, "y": start_y}),
            "end": cmd.end.model_copy(update={"x": end_x, "y": end_y}),
        }
    )


def _clarify_rect(index: int, cmd: DrawRect, session: SessionMemory, followups: List[FollowUpQuestion]) -> DrawRect:
    width = _resolve_numeric(
        session,
        index,
        "rect.width",
        cmd.width,
        "What width should the rectangle have?",
        followups,
    )
    height = _resolve_numeric(
        session,
        index,
        "rect.height",
        cmd.height,
        "What height should the rectangle have?",
        followups,
    )

    anchor_key = f"rect.{cmd.anchor}.x"
    pos_x = _resolve_numeric(
        session,
        index,
        anchor_key,
        cmd.position.x,
        f"Provide the rectangle {cmd.anchor} X coordinate.",
        followups,
    )
    pos_y = _resolve_numeric(
        session,
        index,
        anchor_key.replace(".x", ".y"),
        cmd.position.y,
        f"Provide the rectangle {cmd.anchor} Y coordinate.",
        followups,
    )

    return cmd.model_copy(
        update={
            "width": width,
            "height": height,
            "position": cmd.position.model_copy(update={"x": pos_x, "y": pos_y}),
        }
    )


def clarify(commands: Iterable[CommandType], session: SessionMemory) -> ReadyCommands | List[FollowUpQuestion]:
    followups: List[FollowUpQuestion] = []
    resolved: List[CommandType] = []

    for index, command in enumerate(commands):
        if isinstance(command, DrawCircle):
            resolved.append(_clarify_circle(index, command, session, followups))
        elif isinstance(command, DrawLine):
            resolved.append(_clarify_line(index, command, session, followups))
        elif isinstance(command, DrawRect):
            resolved.append(_clarify_rect(index, command, session, followups))
        else:  # pragma: no cover - defensive
            resolved.append(command)

    if followups:
        return followups

    return ReadyCommands(commands=resolved)


__all__ = ["clarify", "FollowUpQuestion", "ReadyCommands"]
