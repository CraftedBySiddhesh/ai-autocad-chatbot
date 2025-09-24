# Autocad AI Lab — Stepwise Projects (Stage 1: Text → DXF + Previews)

This repository is a **step-by-step AutoCAD + AI build**. We start simple (**Stage 1**) and layer features on top in later stages (2 → 10).
The goal is to keep each stage **production-ready**, with runnable code and tests.

---

## 🎯 Current Stage: 1 — Natural Language → 2D DXF (Offline, Rule-based)

Type plain English like:

```
draw a 50 mm circle at (100,100) and a line from 0,0 to 200,0; save as demo.dxf
```

The app parses the sentence and **generates a DXF** (no AutoCAD required).
Optionally, add `--preview` to save a quick PNG image alongside the DXF.

---

## ✅ Supported Commands (Stage 1.1)

- **Circle**
  `draw a circle radius 50 at (100,100)`
  `draw a 4 inch circle at (0,0)` (unit conversion inch → mm)

- **Line**
  `draw a line from 0,0 to 100,50`

- **Rectangle**
  `draw a rectangle width 80 height 40 at (10,10)`
  `draw a rectangle at (20,20)` → defaults to **100×100 mm**

- **Arc**
  `draw an arc radius 40 mm at (0,0) from 0 to 180`

- **Polyline**
  `polyline points: (0,0) (50,0) (50,50)`
  `polyline closed points: 0,0  100,0  100,50  0,50`

- **Ellipse**
  `ellipse center (0,0) rx 80 mm ry 40 mm rot 15`

- **Text**
  `text "Kitchen" at (100,200) height 50 mm`

- **Multiple commands** joined with `and`, `;`, or newlines
- **Save as**: `save as <filename>.dxf` (appearing anywhere in the text)

**Output:** saved under `outputs/` unless you pass an absolute/relative path in the command.
If you use `--preview`, a `.png` preview is also generated.

---

## 🧩 Tech Stack (Stage 1.1)

- Python 3.11+
- [ezdxf](https://github.com/mozman/ezdxf) for DXF generation
- [matplotlib](https://matplotlib.org/) for PNG previews
- Pure **rule-based parser** (regex); LLM integration comes in later stages

---

## 🚀 Quickstart (Windows / macOS / Linux)

```bash
# 1) Create venv
python -m venv .venv

# 2) Activate
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Run (CLI)
python app/main.py "draw a 50 mm circle at (100,100); draw a line from 0,0 to 200,0; save as demo.dxf" --preview

# 5) Check output
# → outputs/demo.dxf
# → outputs/demo.png
```

**Run tests**
```bash
pytest -q
```

---

## 🗺️ Roadmap (Stages)

1. **Text → DXF (rule-based)** ✅
   - Circles, lines, rectangles, arcs, polylines, ellipses, text
   - Unit conversion, sensible defaults, DXF layers, PNG previews, error reporting
2. Clarification engine (ask for missing params), conversation memory
3. 2D boolean ops (union/diff/intersect) using Shapely + PNG previews
4. Blocks & layers library + semantic retrieval of symbols
5. AI LLM parser (LangChain) with graceful fallback to rules
6. Image → 2D (OpenCV + Tesseract), scale inference from dimensions
7. 3D primitives (OCP/OpenCascade): extrude/revolve + STEP export
8. 3D booleans (fuse/cut/common) and previews (PyVista/Open3D)
9. Live AutoCAD session integration (pyautocad / .NET API) and macros
10. Web app platform (FastAPI + simple UI) with multi-user history

Each stage will be tagged: `stage-1`, `stage-2`, … with upgrade notes.

---

## 📂 Project Structure

```
ai_autocad_chatbot/
├─ app/
│  ├─ core/
│  │  ├─ dxf_writer.py
│  │  ├─ nlp_rules.py
│  │  ├─ units.py
│  │  └─ __init__.py
│  ├─ main.py
│  └─ __init__.py
├─ examples/
│  └─ sample_commands.txt
├─ outputs/
│  └─ .gitkeep
├─ tests/
│  └─ test_parser.py
├─ .github/
│  └─ workflows/
│     └─ ci.yml
├─ .editorconfig
├─ .gitattributes
├─ .gitignore
├─ .pre-commit-config.yaml
├─ LICENSE
├─ README.md
├─ requirements.txt
├─ requirements-dev.txt
└─ pyproject.toml

```

---

## 📝 License
MIT
