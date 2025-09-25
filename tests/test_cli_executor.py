import ezdxf

from app.cli.executor import execute_commands
from app.dsl.llm_parser import LLMParser
from app.dsl.llm_provider import BaseLLMProvider


class StaticProvider(BaseLLMProvider):
    def parse(self, text, schema, *, context=None):  # pragma: no cover - simple stub
        return {
            "commands": [
                {
                    "type": "draw_circle",
                    "center": {"x": 10, "y": 10, "system": "absolute"},
                    "radius": 5,
                    "radius_unit": "mm",
                }
            ]
        }


def test_execute_commands_rule_only(tmp_path):
    out = tmp_path / "rule.dxf"
    path = execute_commands(
        ["draw a line from 0,0 to 100,0"], output=out, enable_ai=False, interactive=False
    )
    doc = ezdxf.readfile(path)
    assert any(entity.dxftype() == "LINE" for entity in doc.modelspace())


def test_execute_commands_ai_with_provider(tmp_path):
    parser = LLMParser(provider=StaticProvider())
    out = tmp_path / "ai.dxf"
    path = execute_commands(
        ["please sketch a small circle"],
        output=out,
        enable_ai=True,
        interactive=False,
        parser=parser,
    )
    doc = ezdxf.readfile(path)
    assert any(entity.dxftype() == "CIRCLE" for entity in doc.modelspace())
