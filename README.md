# AI AutoCAD Chatbot

[![CI](https://github.com/ai-autocad-chatbot/ai-autocad-chatbot/actions/workflows/ci.yml/badge.svg)](https://github.com/ai-autocad-chatbot/ai-autocad-chatbot/actions/workflows/ci.yml)

A conversational assistant that turns natural language or sketches into CAD deliverables. This repository is
being developed in staged milestones; the current focus is establishing deterministic tooling, configuration,
and a minimal CAD core that can emit DXF geometry.

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

## Project Structure

```
ai-autocad-chatbot/
├─ app/
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
│  └─ __init__.py
├─ outputs/
│  └─ .gitkeep
├─ tests/
│  ├─ test_dxf_writer.py
│  ├─ test_parser.py
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
├─ requirements-dev.in
├─ requirements-dev.txt
├─ requirements.in
└─ requirements.txt
```

## License

MIT
