import time

import pytest

from app.dsl.clarify import ReadyCommands, clarify
from app.dsl.commands import Coordinate, DrawCircle
from app.dsl.errors import E_MEMORY_EXPIRED, ParseError
from app.memory.session import SessionMemory
from app.memory.store import ProjectMemoryStore


def test_clarify_generates_followups(tmp_path):
    store = ProjectMemoryStore(tmp_path / "memory.json")
    session = SessionMemory(store=store, project_id="demo")
    command = DrawCircle()
    result = clarify([command], session)
    assert isinstance(result, list)
    prompts = {q.field for q in result}
    assert {"circle.radius", "circle.center.x", "circle.center.y"} <= prompts


def test_clarify_applies_answers_and_persists_defaults(tmp_path):
    store = ProjectMemoryStore(tmp_path / "memory.json")
    session = SessionMemory(store=store, project_id="demo")

    # First pass asks for information
    command = DrawCircle()
    followups = clarify([command], session)
    for q in followups:
        session.set(
            q.id, {"circle.radius": 15, "circle.center.x": 3, "circle.center.y": 4}.get(q.field, 0)
        )

    ready = clarify([command], session)
    assert isinstance(ready, ReadyCommands)
    assert ready.commands[0].radius == 15
    assert ready.commands[0].center.x == 3
    assert ready.commands[0].center.y == 4

    # Next command should reuse defaults when asked to
    next_command = DrawCircle(radius=None, center=Coordinate(x=None, y=None))
    session.set("answer.0.circle.radius", "use previous value")
    session.set("answer.0.circle.center.x", "use previous value")
    session.set("answer.0.circle.center.y", "use previous value")
    ready_again = clarify([next_command], session)
    assert isinstance(ready_again, ReadyCommands)
    assert ready_again.commands[0].radius == 15
    assert ready_again.commands[0].center.x == 3


def test_session_ttl_expiration(tmp_path):
    store = ProjectMemoryStore(tmp_path / "memory.json")
    session = SessionMemory(store=store, ttl=0.05)
    session.set("transient", 42)
    time.sleep(0.06)
    with pytest.raises(ParseError) as exc:
        session.get("transient")
    assert exc.value.code == E_MEMORY_EXPIRED[0]
