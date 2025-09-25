"""In-memory session store with TTL semantics."""
from __future__ import annotations

import time
from typing import Any, Dict, Tuple

from app.dsl.errors import E_MEMORY_EXPIRED, raise_error
from .store import ProjectMemoryStore


class SessionMemory:
    def __init__(
        self,
        *,
        ttl: float = 600.0,
        store: ProjectMemoryStore | None = None,
        project_id: str = "default",
    ) -> None:
        self.ttl = ttl
        self.store = store
        self.project_id = project_id
        self._data: Dict[str, Tuple[Any, float | None]] = {}
        self._defaults: Dict[str, Any] = store.load_project(project_id) if store else {}

    def _expiry_for(self, ttl: float | None) -> float | None:
        effective_ttl = self.ttl if ttl is None else ttl
        if effective_ttl <= 0:
            return None
        return time.time() + effective_ttl

    def set(self, key: str, value: Any, *, ttl: float | None = None, persist: bool = False) -> None:
        self._data[key] = (value, self._expiry_for(ttl))
        if persist:
            self.remember_default(key, value)

    def get(self, key: str, default: Any | None = None) -> Any:
        if key in self._data:
            value, expires = self._data[key]
            if expires is not None and expires < time.time():
                self._data.pop(key, None)
                raise_error(E_MEMORY_EXPIRED, detail=f"Key '{key}' expired.")
            return value
        if key in self._defaults:
            return self._defaults[key]
        return default

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def pop(self, key: str, default: Any | None = None) -> Any:
        if key not in self._data:
            return default
        value, _ = self._data.pop(key)
        return value

    def remember_default(self, key: str, value: Any) -> None:
        self._defaults[key] = value
        if self.store:
            self.store.set_value(self.project_id, key, value)

    def get_default(self, key: str, default: Any | None = None) -> Any:
        return self._defaults.get(key, default)

    def clear(self) -> None:  # pragma: no cover - utility
        self._data.clear()


__all__ = ["SessionMemory"]
