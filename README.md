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

## Units & Precision

Length conversions live in [`app/core/units.py`](app/core/units.py) and rely on `decimal.Decimal` for stable
rounding. Helper functions include `parse_length`, `to_mm`, `from_mm`, and `convert_length`, all quantized to
±1e-6 mm.

## CAD Core

Stage 03 introduces typed models for 2D primitives and a DXF writer:

- [`app/cad/models.py`](app/cad/models.py) defines `Point`, `Line`, `Circle`, and `Rect`.
- [`app/cad/writer.py`](app/cad/writer.py) wraps `ezdxf` and ensures entities land on the `A-GEOM` layer.
- [`app/cad/cli.py`](app/cad/cli.py) ships a `--demo` command that generates `out/demo_stage3.dxf`.

The regression suite verifies unit conversions, configuration parsing, DXF authoring, and package importability.

## Language Understanding

The Stage 04 deterministic DSL and the Stage 05 LLM parser provide layered natural language
understanding:

- [`app/dsl/rules.py`](app/dsl/rules.py) enumerates ten canonical utterance templates covering
  lines, circles, and rectangles with absolute or relative coordinates.
- [`app/dsl/parse_rule.py`](app/dsl/parse_rule.py) compiles the regex rules into
  Pydantic-backed [`Command`](app/dsl/commands.py) models and produces actionable validation
  errors documented in [`docs/errors.md`](docs/errors.md).
- [`app/dsl/llm_provider.py`](app/dsl/llm_provider.py) configures the selected language model
  provider from environment variables, while [`app/dsl/llm_parser.py`](app/dsl/llm_parser.py)
  applies guarded prompting, schema enforcement, and automatic retries. The corresponding
  contract lives in [`docs/prompt_contract.json`](docs/prompt_contract.json).

## Clarification & Memory

Stage 06 introduces a clarification engine and multi-tiered memory to bridge incomplete user
utterances:

- [`app/dsl/clarify.py`](app/dsl/clarify.py) detects missing command fields and generates
  targeted follow-up questions, merging answers into ready-to-execute commands.
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
│  ├─ cad/
│  │  ├─ __init__.py
│  │  ├─ cli.py
│  │  ├─ models.py
│  │  └─ writer.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ config.py
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
