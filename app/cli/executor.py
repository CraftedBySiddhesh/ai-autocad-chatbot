"""Command line execution helpers for the natural language interface."""

from __future__ import annotations

import sys
from collections.abc import Iterable, Sequence
from pathlib import Path

from dotenv import load_dotenv

from app.cad.models import DrawingBundle
from app.cad.writer import DxfWriter
from app.core.config import get_settings
from app.core.conversion import program_to_bundle
from app.core.nlp_rules import Program
from app.core.nlp_rules import parse as legacy_parse
from app.core.units import Unit
from app.dsl.clarify import FollowUpQuestion, ReadyCommands, clarify
from app.dsl.compiler import CommandCompiler
from app.dsl.errors import ParseError
from app.dsl.llm_parser import LLMParser
from app.dsl.llm_provider import configure_provider
from app.memory.session import SessionMemory

_FOLLOWUP_DEFAULTS: dict[str, float] = {
    "circle.radius": 10.0,
    "circle.center.x": 0.0,
    "circle.center.y": 0.0,
    "line.start.x": 0.0,
    "line.start.y": 0.0,
    "line.end.x": 100.0,
    "line.end.y": 0.0,
    "rect.width": 100.0,
    "rect.height": 100.0,
    "rect.corner.x": 0.0,
    "rect.corner.y": 0.0,
    "rect.center.x": 0.0,
    "rect.center.y": 0.0,
}


def _program_has_entities(program: Program) -> bool:
    return bool(
        program.circles
        or program.lines
        or program.rects
        or program.arcs
        or program.polylines
        or program.ellipses
        or program.texts
    )


def _resolve_followups(
    followups: list[FollowUpQuestion],
    session: SessionMemory,
    *,
    interactive: bool,
) -> None:
    for question in followups:
        default = _FOLLOWUP_DEFAULTS.get(question.field, 0.0)
        if interactive and sys.stdin.isatty():
            try:
                answer = input(f"{question.prompt} ")
            except EOFError:
                answer = ""
            value = answer if answer.strip() else default
        else:
            value = default
        session.set(question.id, value)


def _process_with_ai(
    utterance: str,
    parser: LLMParser,
    compiler: CommandCompiler,
    session: SessionMemory,
    *,
    interactive: bool,
) -> DrawingBundle | None:
    try:
        commands = parser.parse(utterance, context={"units": compiler.default_unit.value})
    except ParseError:
        return None

    while True:
        resolution = clarify(commands, session)
        if isinstance(resolution, ReadyCommands):
            ready = resolution.commands
            break
        _resolve_followups(resolution, session, interactive=interactive)
    return compiler.compile(ready)


def _write_bundle(bundle: DrawingBundle, path: Path) -> Path:
    writer = DxfWriter()
    for line in bundle.lines:
        writer.add_line(line)
    for circle in bundle.circles:
        writer.add_circle(circle)
    for rect in bundle.rects:
        writer.add_rect(rect)
    for poly in bundle.polylines:
        writer.add_polyline(poly)
    for arc in bundle.arcs:
        writer.add_arc(arc)
    for ellipse in bundle.ellipses:
        writer.add_ellipse(ellipse)
    for text in bundle.texts:
        writer.add_text(text)
    return writer.save(path)


def execute_commands(
    commands: Sequence[str],
    *,
    output: Path,
    enable_ai: bool = True,
    interactive: bool | None = None,
    parser: LLMParser | None = None,
) -> Path:
    """Process commands and emit a DXF file."""

    load_dotenv()
    interactive = bool(interactive if interactive is not None else sys.stdin.isatty())

    settings = get_settings()
    default_unit = Unit.from_string(settings.DEFAULT_UNITS, default=Unit.MILLIMETER)

    bundle = DrawingBundle()
    session = SessionMemory()
    compiler = CommandCompiler(default_unit=default_unit)

    active_parser = parser
    if enable_ai and active_parser is None:
        try:
            provider = configure_provider()
        except ParseError:
            active_parser = None
        else:
            active_parser = LLMParser(provider=provider)

    for utterance in commands:
        if not utterance.strip():
            continue
        program = legacy_parse(utterance)
        if _program_has_entities(program):
            bundle.extend(program_to_bundle(program))
            continue
        if active_parser is None:
            continue
        ai_bundle = _process_with_ai(
            utterance, active_parser, compiler, session, interactive=interactive
        )
        if ai_bundle:
            bundle.extend(ai_bundle)

    if not any(bundle.iter_all()):
        raise RuntimeError("No drawable entities were produced from the provided commands.")

    return _write_bundle(bundle, output)


def load_commands(cmd: str | None, stdin_stream: Iterable[str]) -> list[str]:
    if cmd:
        return [cmd.strip()]

    if not sys.stdin.isatty():
        return [line.strip() for line in stdin_stream if line.strip()]

    print("Enter drawing commands (Ctrl-D to finish):")
    collected: list[str] = []
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if line.strip():
            collected.append(line.strip())
    return collected


__all__ = ["execute_commands", "load_commands"]
