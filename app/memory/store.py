"""Project scoped persistence for clarification defaults."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ProjectMemoryStore:
    """Simple JSON backed key-value store keyed by project identifier."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({})

    def _read(self) -> Dict[str, Dict[str, Any]]:
        with self.path.open("r", encoding="utf8") as fh:
            return json.load(fh)

    def _write(self, data: Dict[str, Dict[str, Any]]) -> None:
        with self.path.open("w", encoding="utf8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)

    def load_project(self, project_id: str) -> Dict[str, Any]:
        data = self._read()
        return data.get(project_id, {}).copy()

    def set_value(self, project_id: str, key: str, value: Any) -> None:
        data = self._read()
        project = data.setdefault(project_id, {})
        project[key] = value
        self._write(data)

    def delete_value(self, project_id: str, key: str) -> None:
        data = self._read()
        project = data.get(project_id)
        if project and key in project:
            project.pop(key)
            self._write(data)


__all__ = ["ProjectMemoryStore"]
