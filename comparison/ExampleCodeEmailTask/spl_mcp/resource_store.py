"""Lightweight in-process MCP resource store for the SPL POC."""

from __future__ import annotations

from typing import Any, Dict
import copy


class ResourceStore:
    """In-memory resource registry keyed by resource_id."""

    def __init__(self):
        self._store: Dict[str, Any] = {}

    def read(self, resource_id: str) -> Any:
        """Read a resource by id, returning a deep copy to avoid mutation leaks."""
        if resource_id not in self._store:
            raise KeyError(f"Resource not found: {resource_id}")
        return copy.deepcopy(self._store[resource_id])

    def write(self, resource_id: str, payload: Any) -> None:
        """Persist a resource payload."""
        self._store[resource_id] = copy.deepcopy(payload)

    def ensure(self, resource_id: str, default: Any) -> Any:
        """Ensure a resource exists, writing default if missing, and return its value."""
        if resource_id not in self._store:
            self.write(resource_id, default)
        return self.read(resource_id)
