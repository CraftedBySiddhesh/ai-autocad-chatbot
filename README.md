# AI AutoCAD Chatbot

[![CI](https://github.com/ai-autocad-chatbot/ai-autocad-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/ai-autocad-chatbot/ai-autocad-chatbot/actions/workflows/ci.yml)

A conversational assistant that turns natural language or sketches into CAD deliverables. This repository is
being developed in staged milestones; the current focus is establishing deterministic tooling, configuration,
and a minimal CAD core that can emit DXF geometry. Stages 04–06 add a deterministic
mini-DSL, an LLM-backed parser, and clarification/memory components that blend rule-based
and generative understanding.

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
make setup
```

Useful commands:

- `make setup` – install runtime + development dependencies.
- `make lint` – run Ruff, Black, and Isort in check mode.
- `make type` – execute mypy over the `app` package.
- `make test` – execute the pytest suite.
- `make fix` – auto-format with isort/black/ruff.
- `make lock` – regenerate pinned requirements via pip-tools.

## Configuration

Runtime configuration is handled by [`app/core/config.py`](app/core/config.py). Copy `.env.example` to `.env` and
adjust settings as needed. Supported keys:

- `DEFAULT_UNITS` – controls default parsing/export units (`mm` or `in`).
- `AI_PROVIDER` – selects the LLM backend (`mock`, `openai`, `groq`, `llama3`).
- `AI_MODEL` – optional model override for the active provider.
- `AI_API_KEY` – API token for hosted LLM providers (unused by the mock provider).
- `AI_TEMPERATURE` – optional float to control sampling temperature.
  Legacy variables `AI_AUTOCAD_PROVIDER` and `AI_AUTOCAD_API_KEY` remain supported for compatibility.

## Units & Precision

Length conversions live in [`app/core/units.py`](app/core/units.py) and rely on `decimal.Decimal` for stable
rounding. Helper functions include `parse_length`, `to_mm`, `from_mm`, and `convert_length`, all quantized to
±1e-6 mm.

## CAD Core

Stage 03 introduces typed models for 2D primitives and a DXF writer. The current release extends these pieces to
cover the full geometry set required by the hybrid CLI:

- [`app/cad/models.py`](app/cad/models.py) defines `Point`, `Line`, `Circle`, `Rect`, `Polyline`, `Arc`, `Ellipse`,
  and `Text` entities. `DrawingBundle` is used to stage heterogeneous geometry prior to writing.
- [`app/cad/writer.py`](app/cad/writer.py) wraps `ezdxf` and ensures entities land on the `A-GEOM` layer.
- [`app/core/conversion.py`](app/core/conversion.py) converts legacy rule-parser output into the new CAD bundle.

The regression suite verifies unit conversions, configuration parsing, DXF authoring, and the hybrid parsing flow.

## Command Line Interface

Run `python -m app.main --cmd "draw a line from 0,0 to 100,50"` to process a single command. When `--cmd` is not
provided the CLI reads one command per line from standard input until EOF. The `--no-ai` flag forces deterministic
regex parsing only, while `--non-interactive` suppresses clarification prompts and falls back to sensible defaults.

Example session with AI clarification enabled:

```
$ python -m app.main
Enter drawing commands (Ctrl-D to finish):
> draw rectangle at 50,50
# CLI prompts for the missing width/height and corner coordinates here.
> make a square 20
DXF saved to: outputs/cli_output.dxf
```

## Language Understanding

The Stage 04 deterministic DSL and the Stage 05 LLM parser provide layered natural language
understanding:

- [`app/dsl/rules.py`](app/dsl/rules.py) enumerates ten canonical utterance templates covering
  lines, circles, and rectangles with absolute or relative coordinates.
- [`app/dsl/parse_rule.py`](app/dsl/parse_rule.py) compiles the regex rules into
  Pydantic-backed [`Command`](app/dsl/commands.py) models and produces actionable validation
  errors documented in [`docs/errors.md`](docs/errors.md).
- [`app/ai/providers.py`](app/ai/providers.py) registers LangChain chat providers (OpenAI, Groq, Llama3) with the
  shared registry exposed by [`app/dsl/llm_provider.py`](app/dsl/llm_provider.py).
- [`app/dsl/llm_parser.py`](app/dsl/llm_parser.py)
  applies guarded prompting, schema enforcement, and automatic retries. The corresponding
  contract lives in [`docs/prompt_contract.json`](docs/prompt_contract.json).
- [`app/dsl/compiler.py`](app/dsl/compiler.py) normalises LLM output into CAD primitives stored in millimetres.

## Clarification & Memory

Stage 06 introduces a clarification engine and multi-tiered memory to bridge incomplete user
utterances:

- [`app/dsl/clarify.py`](app/dsl/clarify.py) detects missing command fields and generates
  targeted follow-up questions, merging answers into ready-to-execute commands. Example
  dialog flows are captured in [`docs/clarification.md`](docs/clarification.md).
- [`app/memory/session.py`](app/memory/session.py) and [`app/memory/store.py`](app/memory/store.py)
  provide session-scoped defaults and project persistence to reuse prior context.

## Project Structure

```
ai-autocad-chatbot/
├─ app/
│  ├─ dsl/
│  │  ├─ __init__.py
│  │  ├─ clarify.py
│  │  ├─ commands.py
│  │  ├─ errors.py
│  │  ├─ llm_parser.py
│  │  ├─ llm_provider.py
│  │  ├─ parse_rule.py
│  │  └─ rules.py
│  ├─ ai/
│  │  ├─ __init__.py
│  │  └─ providers.py
│  ├─ cad/
│  │  ├─ __init__.py
│  │  ├─ models.py
│  │  └─ writer.py
│  ├─ cli/
│  │  ├─ __init__.py
│  │  └─ executor.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py
│  │  ├─ conversion.py
│  │  ├─ dxf_writer.py
│  │  ├─ nlp_rules.py
│  │  └─ units.py
│  ├─ memory/
│  │  ├─ __init__.py
│  │  ├─ session.py
│  │  └─ store.py
│  └─ __init__.py
├─ outputs/
│  └─ .gitkeep
├─ tests/
│  ├─ test_clarify.py
│  ├─ test_dxf_writer.py
│  ├─ test_llm_parser.py
│  ├─ test_parser.py
│  ├─ test_rule_parser.py
│  ├─ test_sanity.py
│  └─ test_units.py
├─ .github/workflows/ci.yml
├─ .editorconfig
├─ .gitattributes
├─ .gitignore
├─ .pre-commit-config.yaml
├─ Makefile
├─ README.md
├─ constraints.txt
├─ docs/
│  ├─ errors.md
│  └─ prompt_contract.json
├─ requirements-dev.in
├─ requirements-dev.txt
├─ requirements.in
└─ requirements.txt
```

## License

MIT
